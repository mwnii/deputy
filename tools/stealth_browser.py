"""
Stealth Browser Module — THE ONLY way to launch browsers in this system.

NEVER import playwright directly. Always use this module.

CloakBrowser wraps a patched Chromium binary with 71 C++ source-level
fingerprint modifications. It passes 30/30 bot detection tests including
Cloudflare Turnstile, reCAPTCHA v3 (0.9 score), FingerprintJS, and BrowserScan.

Usage:
    from tools.stealth_browser import launch
    browser = launch(headless=False, humanize=True)
    page = browser.new_page()
    page.goto("https://example.com")
    browser.close()

For persistent sessions (cookies survive restarts):
    from tools.stealth_browser import launch_persistent_context
    ctx = launch_persistent_context("./profile-dir", headless=False)
    page = ctx.new_page()
    page.goto("https://example.com")
    ctx.close()
"""

from cloakbrowser import (
    launch,
    launch_async,
    launch_context,
    launch_context_async,
    launch_persistent_context,
    launch_persistent_context_async,
    binary_info,
    clear_cache,
    ensure_binary,
)

__all__ = [
    "launch",
    "launch_async",
    "launch_context",
    "launch_context_async",
    "launch_persistent_context",
    "launch_persistent_context_async",
    "binary_info",
    "clear_cache",
    "ensure_binary",
]


def verify_stealth():
    """Quick check that CloakBrowser binary is installed and ready."""
    info = binary_info()
    if not info.get("installed"):
        raise RuntimeError(
            f"CloakBrowser binary not installed. Run: python -m cloakbrowser install"
        )
    return info


# Verify on import so failures are caught immediately
verify_stealth()
