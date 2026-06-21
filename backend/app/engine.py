"""The single execution path for every SpotHound target.

A real browser (Playwright) opens the page, runs a sequence of steps
(clicks / selects / waits), then evaluates one condition. Because it drives a
real browser with an anti-bot context, the same engine handles plain pages,
JSON-API apps, and JavaScript sites that block headless browsers.

This module depends only on Playwright so it can be exercised standalone
(see selftest.py) without the database or web app.
"""
from __future__ import annotations

from typing import Any

from playwright.sync_api import sync_playwright

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_HIDE_WEBDRIVER = "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"

# Decides whether an element is "disabled" across the common patterns:
# a native [disabled] attribute, aria-disabled="true", or a class that
# contains "disabled" / "disbled" (some sites misspell it, e.g. Yodel).
_INSPECT_JS = """
(el) => {
  const cls = (el.className || '').toString().toLowerCase();
  const disabled =
    el.hasAttribute('disabled') ||
    el.getAttribute('aria-disabled') === 'true' ||
    cls.includes('disbled') || cls.includes('disabled');
  return { disabled, text: (el.textContent || '').trim().slice(0, 200) };
}
"""


def run_check(
    url: str,
    steps: list[dict[str, Any]] | None = None,
    condition: dict[str, Any] | None = None,
    headless: bool = True,
    nav_timeout: int = 45000,
) -> dict[str, Any]:
    """Open the page, run the steps, evaluate the condition.

    Returns {"met": bool, "observed": str | None, "error": str | None}.
    `met` is True when the condition is satisfied (i.e. time to notify).
    """
    steps = steps or []
    condition = condition or {}
    result: dict[str, Any] = {"met": False, "observed": None, "error": None}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        ctx = browser.new_context(
            user_agent=DEFAULT_UA,
            locale="en-US",
            viewport={"width": 1280, "height": 900},
        )
        ctx.add_init_script(_HIDE_WEBDRIVER)
        page = ctx.new_page()
        try:
            page.goto(url, timeout=nav_timeout, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)  # let SPA fire its initial requests
            for step in steps:
                _run_step(page, step)
            result.update(_eval_condition(page, condition))
        except Exception as exc:  # noqa: BLE001 — surface any failure as text
            result["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            browser.close()
    return result


def _run_step(page, step: dict[str, Any]) -> None:
    action = step.get("action")
    selector = step.get("selector")
    timeout = step.get("timeout", 15000)

    if action == "click":
        page.click(selector, timeout=timeout)
    elif action == "select":
        if "label" in step:
            page.select_option(selector, label=step["label"], timeout=timeout)
        else:
            page.select_option(selector, value=step["value"], timeout=timeout)
    elif action == "fill":
        page.fill(selector, step.get("text", ""), timeout=timeout)
    elif action == "wait":
        if selector:
            page.wait_for_selector(selector, timeout=timeout)
        else:
            page.wait_for_timeout(step.get("ms", 1000))
    else:
        raise ValueError(f"Unknown step action: {action!r}")


def _eval_condition(page, condition: dict[str, Any]) -> dict[str, Any]:
    """Supported checks: enabled, disabled, exists, not_exists,
    text_present, text_absent. `value` is the comparison text where relevant."""
    check = condition.get("check")
    selector = condition.get("selector")
    value = condition.get("value")

    if check in ("exists", "not_exists"):
        count = page.locator(selector).count()
        exists = count > 0
        met = exists if check == "exists" else not exists
        return {"met": met, "observed": f"exists={exists} (count={count})"}

    locator = page.locator(selector).first
    try:
        locator.wait_for(timeout=8000, state="attached")
    except Exception:
        return {"met": False, "observed": "element not found"}

    info = locator.evaluate(_INSPECT_JS)
    disabled, text = info["disabled"], info["text"]

    if check == "enabled":
        return {"met": not disabled, "observed": f"disabled={disabled}, text={text!r}"}
    if check == "disabled":
        return {"met": disabled, "observed": f"disabled={disabled}, text={text!r}"}
    if check == "text_present":
        return {"met": (value or "") in text, "observed": f"text={text!r}"}
    if check == "text_absent":
        return {"met": (value or "") not in text, "observed": f"text={text!r}"}

    raise ValueError(f"Unknown condition check: {check!r}")
