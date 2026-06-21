# Adding a new spot

A **spot** is a code-defined recipe for checking one thing on one site. Adding
one is a developer task (best done with Claude). End users then just enable it
and set scheduling/subscribers in the UI — they never write this.

This is the repeatable workflow. Budget ~15 minutes per site.

---

## 1. Understand the page

Open the page in a normal browser with DevTools → **Network** tab, and do the
clicks a human would do to reach the "is it available?" state. You're looking
for one of two things:

- **The element that signals availability** — usually a button/radio/link that
  is *disabled* (greyed out) when full and *enabled* when open. Note a stable
  CSS selector for it (an `id`, `aria-label`, or unique class).
- **The clicks needed to get there** — e.g. "Book a Pass" → open date picker →
  pick the date → choose a lot.

> SpotHound always uses the browser engine, so you generally drive the visible
> UI. (If the site has a clean JSON API you *may* point the URL straight at it,
> but the browser flow is the default and most robust.)

### Capture script (optional but handy)

To dump a site's API/XHR calls and confirm how it loads, adapt this throwaway
script (Playwright is already a dependency):

```python
# scratch_capture.py  — run: cd backend && uv run python scratch_capture.py
import asyncio
from playwright.async_api import async_playwright

URL = "https://example.com/the-page"

async def main():
    async with async_playwright() as p:
        # headless=False if the site blocks bots (403 / "Forbidden")
        browser = await p.chromium.launch(headless=False,
                    args=["--disable-blink-features=AutomationControlled"])
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        await ctx.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page = await ctx.new_page()
        page.on("response", lambda r: "application/json" in r.headers.get("content-type","")
                 and print(r.request.method, r.url))
        await page.goto(URL, timeout=40000)
        await page.wait_for_timeout(6000)
        await browser.close()

asyncio.run(main())
```

If the page text shows **403 / Forbidden** under headless, the site has bot
detection → the spot must use `headless=False`.

## 2. Translate it into steps + a condition

**Steps** (run in order after the page loads). Each needs a `selector`:

| action | fields | meaning |
|---|---|---|
| `click` | `selector` | click an element |
| `select` | `selector`, `label` or `value` | choose a `<select>` option |
| `fill` | `selector`, `text` | type into an input |
| `wait` | `ms` *or* `selector` | pause, or wait for an element |

**Condition** — the single thing that means "available now":

| check | meaning |
|---|---|
| `enabled` | element is NOT disabled (notify when it becomes clickable) |
| `disabled` | element IS disabled |
| `exists` / `not_exists` | element present / absent |
| `text_present` / `text_absent` | `value` is / isn't in the element's text |

`enabled`/`disabled` treat all of these as "disabled": a native `disabled`
attribute, `aria-disabled="true"`, or a class containing `disabled`/`disbled`.

## 3. Write the spot module

Create `backend/app/spots/<key>.py`. The `key` is a permanent snake_case id
(also the filename) — **never rename it**, it's the link to the DB row.

```python
"""<Site> — <what this checks>.

Discovery notes: how you found the selectors, whether it needs headful,
any reCAPTCHA/bot-detection, and what's fragile (date-specific selectors, etc.).
"""
from .base import SpotDefinition

SPOT = SpotDefinition(
    key="my_site_thing",
    name="My Site — The Thing (Sun Jun 21)",
    url="https://example.com/the-page",
    headless=True,            # False if the site 403s headless browsers
    default_interval_seconds=120,
    steps=[
        {"action": "wait", "ms": 3000},
        {"action": "click", "selector": "button.choose-date"},
    ],
    condition={"selector": "button.add-to-cart", "check": "enabled"},
)
```

The registry auto-discovers it — no other code to touch. Look at the two
existing modules for reference:

- `backend/app/spots/bc_parks_alouette_pm.py` — easy site (no bot detection)
- `backend/app/spots/buntzen_lake_all_day.py` — hard site (headful + reCAPTCHA)

## 4. Test it (no database needed)

```bash
make selftest spot=my_site_thing
```

Expect `observed:` to describe the element and `MET (would notify): False`
while it's full. If it errors, fix the selectors/steps. For bot-detected sites,
confirm `headless=False`.

## 5. Sync it into the app

The new target appears (disabled) on next app start, or immediately via:

```
POST /admin/sync-spots      # admin token
```

Then in the UI/API: enable it, set the interval/schedule, and add subscribers.

---

## Gotchas

- **Date-specific selectors** (`aria-label="Sunday, June 21, 2026"`,
  `aria-label="Sunday 21"`) only match one day — update `steps` when the target
  date changes. (A future enhancement could templatize the date.)
- **Poll bot-protected sites gently** — every few minutes, not every minute, to
  avoid tripping rate limits. Set `default_interval_seconds` accordingly.
- **reCAPTCHA** usually guards only the *purchase*, not viewing availability.
  SpotHound only detects and notifies; the human completes the booking.
- **Keep the `notes`** current — they're how we remember why a recipe looks the
  way it does when a site changes and the check breaks.
