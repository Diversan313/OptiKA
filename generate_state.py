from playwright.sync_api import sync_playwright
import base64
from pathlib import Path


def main():
    print("=" * 60)
    print("  OptikLink panel session setup")
    print("=" * 60)
    print()
    print("This script creates a browser storage state file")
    print("that GitHub Actions later uses to keep the server")
    print("alive and start it when needed.")
    print()

    # --- Proxy prompt ---
    use_proxy = input(
        "Do you need a proxy? (if the site is not reachable directly). [y/N]: "
    ).strip().lower()

    proxy_config = None
    if use_proxy in ("y", "yes", "д", "да"):
        port = input(
            "Enter local proxy port (e.g. 10808 or 7890): "
        ).strip()
        if not port.isdigit():
            print("Error: port must be a number. Aborting.")
            return

        proxy_config = {"server": f"http://127.0.0.1:{port}"}
        print(f"\nProxy configured: http://127.0.0.1:{port}")
    else:
        print("\nNo proxy will be used.")

    print()
    print("-" * 60)
    print("Steps:")
    print("1. A browser window will open.")
    print("2. Log in at control.optiklink.net.")
    print("3. After a successful login, return to this terminal")
    print("   and press Enter to continue.")
    print("-" * 60)
    print()
    input("Press Enter to open the browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context_options = {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

        if proxy_config:
            context_options["proxy"] = proxy_config

        context = browser.new_context(**context_options)
        page = context.new_page()

        try:
            page.goto("https://control.optiklink.net", timeout=60000)
        except Exception as e:
            print(f"\nWarning: page could not be loaded automatically ({e}).")
            print("Please refresh the page manually in the browser window.")

        input("\n>>> After a successful login, press Enter... ")

        # Save session state
        context.storage_state(path="state.json")
        browser.close()

    # Build base64 string
    state_bytes = Path("state.json").read_bytes()
    b64 = base64.b64encode(state_bytes).decode("ascii")

    print()
    print("=" * 60)
    print("  Session saved successfully")
    print("=" * 60)
    print()
    print("Copy the string below in full and add it to")
    print("GitHub Secrets as:  STATE_JSON_BASE64")
    print()
    print("-" * 60)
    print(b64)
    print("-" * 60)
    print()
    print("state.json is also saved in the current folder")
    print("in case you need it again.")
    print()


if __name__ == "__main__":
    main()
