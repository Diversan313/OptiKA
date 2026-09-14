import base64
import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


SERVER_ID = os.getenv("SERVER_ID")
PANEL_USER = os.getenv("PANEL_USER")
PANEL_PASSWORD = os.getenv("PANEL_PASSWORD")
STATE_JSON_BASE64 = os.getenv("STATE_JSON_BASE64")
ENABLE_SCREENSHOTS = os.getenv("ENABLE_SCREENSHOTS", "false").lower() in ("1", "true", "yes")

OPTIKLINK_AUTH_URL = "https://optiklink.net/auth"
PANEL_BASE = "https://control.optiklink.net"


def die(message: str, code: int = 1):
    print(f"[ERROR] {message}")
    sys.exit(code)


def take_screenshot(page, name: str):
    if not ENABLE_SCREENSHOTS:
        return
    try:
        page.screenshot(path=f"{name}.png", full_page=True)
        print(f"[*] Screenshot saved: {name}.png")
    except Exception as e:
        print(f"[*] Failed to save screenshot {name}: {e}")


def main():
    if not SERVER_ID:
        die("SERVER_ID secret is not set")

    if STATE_JSON_BASE64:
        try:
            Path("state.json").write_bytes(base64.b64decode(STATE_JSON_BASE64))
            print("[+] Session restored from STATE_JSON_BASE64")
        except Exception as e:
            print(f"[!] Failed to restore session: {e}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context_options = {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

        if Path("state.json").exists():
            context_options["storage_state"] = "state.json"

        context = browser.new_context(**context_options)
        page = context.new_page()

        # 1. Refresh timer
        print("[1/2] Opening OptikLink to refresh the timer...")
        try:
            page.goto(OPTIKLINK_AUTH_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            print("[+] Timer refreshed (or was already active)")
        except Exception as e:
            print(f"[*] Warning while contacting optiklink.net: {e}")
            take_screenshot(page, "error_optiklink")

        # 2. Server page
        server_url = f"{PANEL_BASE}/server/{SERVER_ID}"
        print(f"[2/2] Opening server page: {server_url}")

        try:
            page.goto(server_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"[*] Failed to load server page: {e}")
            take_screenshot(page, "error_server_page")

        page.wait_for_timeout(4000)

        # 3. Login if required
        if "login" in page.url or page.locator('input[type="password"]').is_visible():
            print("[!] Login form detected. Signing in...")

            if not PANEL_USER or not PANEL_PASSWORD:
                take_screenshot(page, "error_no_credentials")
                die("PANEL_USER and/or PANEL_PASSWORD secrets are not set")

            user_input = page.locator(
                'input[type="text"], input[name="username"], input[name="email"]'
            ).first
            pass_input = page.locator('input[type="password"]').first

            user_input.fill(PANEL_USER)
            pass_input.fill(PANEL_PASSWORD)

            login_btn = page.locator(
                'button:has-text("LOGIN"), button[type="submit"]'
            ).first
            login_btn.click()

            try:
                page.wait_for_url(lambda url: "auth/login" not in url, timeout=15000)
                print("[+] Signed in to the panel successfully")
            except PlaywrightTimeout:
                take_screenshot(page, "error_login_failed")
                die("Failed to sign in. Check PANEL_USER and PANEL_PASSWORD")

            page.goto(server_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

        # 4. Start server
        print("[!] Looking for START button...")
        try:
            start_btn = page.locator("button").filter(
                has_text=re.compile(r"^start$", re.IGNORECASE)
            ).first

            if not start_btn.is_visible():
                start_btn = page.locator(
                    'button:has-text("START"), button:has-text("Start")'
                ).first

            if start_btn.is_visible(timeout=10000):
                start_btn.click()
                page.wait_for_timeout(5000)
                print("[+] Server started via the web UI")
            else:
                print("[-] START button not found (server may already be running)")
                print(f"[*] Current URL: {page.url}")
                take_screenshot(page, "error_start_button")
        except Exception as e:
            print(f"[-] Error while clicking START: {e}")
            take_screenshot(page, "error_start_button")

        browser.close()
        print("[+] Script finished")


if __name__ == "__main__":
    main()
