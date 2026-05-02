from playwright.sync_api import sync_playwright
import time
import requests
from datetime import datetime

URL = "https://kktix.com/events/akiba1/registrations/new"
import os
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord(msg):
    try:
        r = requests.post(DISCORD_WEBHOOK, json={"content": msg})
        print("Discord狀態:", r.status_code)
    except Exception as e:
        print("Discord發送失敗:", e)

def check_ticket():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL)
        page.wait_for_timeout(5000)

        content = page.content()

        browser.close()

        if "自行選位" in content or "電腦配位" in content:
            return True

        return False


last_report_time = 0
notified = False  # 👉 控制「只通知一次」

while True:
    try:
        now = time.time()
        has_ticket = check_ticket()

        # 🔥 有票：只通知第一次
        if has_ticket and not notified:
            send_discord("🔥 KKTIX釋票啦！！！快搶！\n" + URL)
            print("🔥 已發送一次通知")
            notified = True

        # 🟡 沒票：每1小時回報
        if not has_ticket:
            if now - last_report_time >= 3600:
                time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_discord(f"🟡 目前無票（{time_str}）\n{URL}")
                print("🟡 每小時回報已發送")
                last_report_time = now
            else:
                print("還沒票（靜默中）")

        # 🧠 如果票又消失，可以重置通知（可選）
        if not has_ticket:
            notified = False

        time.sleep(60)

    except Exception as e:
        print("錯誤：", e)
        time.sleep(60)