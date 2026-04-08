import requests
import time

# 配置
VISIT_DATE = "18/04/2026"
SENDKEY    = "SCT335071T4mVM8yeqsUYpyVOIZpZFjACJ"

# 梵蒂冈公开API 无需TOKEN
URL = f"https://tickets.museivaticani.va/api/search/result?lang=en&visitorNum=2&visitDate={VISIT_DATE}&area=1&who=1&page=0"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://tickets.museivaticani.va/"
}

def wechat_notify(title, content):
    try:
        api = f"https://sctapi.ftqq.com/{SENDKEY}.send"
        requests.post(api, data={"title": title, "desp": content}, timeout=10)
    except:
        pass

def main():
    try:
        r = requests.get(URL, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            print("请求失败")
            return

        data = r.json()
        visits = data.get("visits", [])
        if not visits:
            print("无场次")
            return

        # 只监控第一个场次 visits[0]
        v0 = visits[0]
        status = v0.get("availability")
        desc = v0.get("descrAvailability", "")
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        msg = f"[{now}] 状态: {status}\n{desc}"
        print(msg)

        # ================= 测试微信通知（运行一次就会发） =================
        # wechat_notify("✅ 梵蒂冈监控已上线（测试消息）", "脚本运行正常，有票会自动提醒！")

        # 真正监控逻辑
        if status != "SOLD_OUT":
            wechat_notify("🚨 梵蒂冈门票有票了！", msg)

    except Exception as e:
        print("错误:", e)

if __name__ == "__main__":
    main()
