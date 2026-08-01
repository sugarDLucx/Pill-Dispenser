# Implementation Plan: Telegram Integration & Bluetooth Fix

## Goal
Add Telegram Bot integration as an alternative (or companion) to SMS for Wifi-based control, and fix the Bluetooth auto-connect script which fails because the Bluetooth agent drops when called non-interactively.

## User Review Required
> [!IMPORTANT]
> To use Telegram, you must create a bot via BotFather on Telegram and obtain a **Bot Token**.
> How would you like to provide this token to the Raspberry Pi? 
> Options:
> 1. Store it in a `.env` file (`TELEGRAM_BOT_TOKEN=...`).
> 2. Hardcode it into a config file.

## Open Questions
> [!NOTE]
> Since we are adding Telegram, how should we link a Telegram user to the device? 
> **Proposed Solution:** Anyone who messages the bot will interact with the dispenser. Since the bot token is private to you, this is secure. When you text commands via Telegram, the system will reply via Telegram!

## Proposed Changes

### `backend/hardware_daemon.py`
- Create a `telegram_polling_loop()` thread that uses the `requests` library to poll the Telegram `getUpdates` API.
- Refactor `send_sms(sender, message)` to check if the sender starts with `TG_`. If it does, send the message back via Telegram `sendMessage` API instead of the SIM800L module!
- Parse incoming Telegram messages and pass them into the existing `parse_sms_command("TG_" + chat_id, text)` function. This seamlessly routes all existing logic (add, remove, cool, list) to Telegram!

### `backend/bt_autoconnect.sh`
- Fix the script by using a "Here-Document" (`<<EOF`) to feed commands to `bluetoothctl`. Currently, running `bluetoothctl agent on` in bash immediately closes the interactive shell and kills the agent, which causes `bluetoothctl pair` to fail later on.
- Use `agent NoInputNoOutput` to automatically accept pairing requests for headless speakers.

## Verification Plan
- Verify Bluetooth connects to speakers automatically on boot.
- Verify Telegram bot responds to commands exactly as the SMS system does.
