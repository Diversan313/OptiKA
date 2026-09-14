# OptiKA — OptikLink KeepAlive

**Язык:** [English](README.md) | Русский

Python-скрипт для GitHub Actions, который поддерживает бесплатный сервер OptikLink в рабочем состоянии (`control.optiklink.net`).

С помощью Playwright скрипт:

1. Восстанавливает сохранённую сессию браузера (или выполняет вход по логину/паролю панели при необходимости)
2. Переходит на `optiklink.net/auth` и продлевает 3-дневный таймер активности
3. Открывает страницу сервера и нажимает **START**, если сервер выключен

Так бесплатный сервер не останавливается из-за отсутствия ручного захода более 3 дней.

Может работать вместе с [Optiklink-VLESS](https://github.com/Diversan313/Optiklink-VLESS) или отдельно.

---

## Структура репозитория

| Файл | Назначение |
|------|------------|
| `generate_state.py` | Локальный скрипт для создания сессии (один раз) |
| `autologin.py` | Основной скрипт для GitHub Actions |
| `.github/workflows/keepalive.yml` | Расписание и workflow |

---

## Настройка

### 1. Форк репозитория

Нажмите **Fork**.

### 2. Создание сессии (один раз на своём компьютере)

```bash
pip install playwright
playwright install chromium

python generate_state.py
```

Скрипт спросит про прокси, если сайт недоступен напрямую.  
После успешного входа выдаст длинную строку — это значение секрета `STATE_JSON_BASE64`.

### 3. Секреты

**Settings → Secrets and variables → Actions**:

| Секрет | Обязательный | Описание |
|--------|--------------|----------|
| `SERVER_ID` | Да | ID сервера из URL `/server/XXXX` |
| `STATE_JSON_BASE64` | Да | Строка из `generate_state.py` |
| `PANEL_USER` | Рекомендуется | Логин панели (если сессия протухла) |
| `PANEL_PASSWORD` | Рекомендуется | Пароль панели (если сессия протухла) |
| `ENABLE_SCREENSHOTS` | Нет | `true` — скриншоты при ошибках |

### 4. Запуск

- Автоматически **каждый день в 12:00 UTC** (cron)
- Вручную: **Actions** → **OptikLink KeepAlive** → **Run workflow**

---

## Локальная проверка

```bash
export SERVER_ID=ваш_id_сервера
export STATE_JSON_BASE64=ваша_строка_из_generate_state
# при необходимости:
export PANEL_USER=...
export PANEL_PASSWORD=...
export ENABLE_SCREENSHOTS=true

python autologin.py
```

---

## Важно

Автоматизация входа и действий в панели может нарушать правила сервиса.  
Используйте скрипт на свой страх и риск.
