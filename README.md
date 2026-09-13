# OptiKA — OptikLink KeepAlive

**Language:** English | [Русский](README_RU.md)

Python script for GitHub Actions that keeps an OptikLink free server alive (`control.optiklink.net`).

Using Playwright, the script:

1. Restores a saved browser session (or logs in with panel credentials if needed)
2. Visits `optiklink.net/auth` to refresh the 3-day activity timer
3. Opens the server page and clicks **START** if the server is stopped

This prevents the free server from shutting down due to inactivity.

Works with [Optiklink-VLESS](https://github.com/Diversan313/Optiklink-VLESS) or standalone.

---

## Repository structure

| File | Purpose |
|------|---------|
| `generate_state.py` | One-time local script to create a browser session |
| `autologin.py` | Main script run by GitHub Actions |
| `.github/workflows/keepalive.yml` | Schedule and workflow |

---

## Setup

### 1. Fork the repository

Click **Fork**.

### 2. Create a session (once, on your machine)

```bash
pip install playwright
playwright install chromium

python generate_state.py
```

The script may ask about a proxy if the site is blocked.  
After a successful login it prints a long string — use it as the `STATE_JSON_BASE64` secret.

### 3. Configure secrets

**Settings → Secrets and variables → Actions**:

| Secret | Required | Description |
|--------|----------|-------------|
| `SERVER_ID` | Yes | Server ID from URL `/server/XXXX` |
| `STATE_JSON_BASE64` | Yes | String from `generate_state.py` |
| `PANEL_USER` | Recommended | Panel login (if session expires) |
| `PANEL_PASSWORD` | Recommended | Panel password (if session expires) |
| `ENABLE_SCREENSHOTS` | No | `true` — save screenshots on errors |

### 4. Run

- Automatically every 2 days (cron)
- Manually: **Actions** → **OptikLink KeepAlive** → **Run workflow**

---

## Local test

```bash
export SERVER_ID=your_server_id
export STATE_JSON_BASE64=your_string_from_generate_state
# optional:
export PANEL_USER=...
export PANEL_PASSWORD=...
export ENABLE_SCREENSHOTS=true

python autologin.py
```

---

## Disclaimer

Automating login and actions on a control panel may violate the service terms of use.  
Use this script at your own risk.

