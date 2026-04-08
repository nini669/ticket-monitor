import requests
import time

# 你的配置信息
VISIT_DATE = "18/04/2026"
SENDKEY = "SCT335071T4mVM8yeqsUYpyVOIZpZFjACJ"

# 梵蒂冈门票API
URL = (
    f"https://tickets.museivaticani.va/api/search/result"
    f"?lang=en&visitorNum=2&visitDate={VISIT_DATE}&area=1&who=1&page=0"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://tickets.museivaticani.va/"
}

def wechat_notify(title, content):
    """通过Server酱发送微信通知"""
    api = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": content}
    try:
        requests.post(api, data=data, timeout=10)
    except Exception as e:
        print(f"微信通知失败: {e}")

def check_tickets():
    """检查门票状态"""
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return

        data = response.json()
        visits = data.get("visits", [])
        if not visits:
            print("暂无场次信息")
            return

        # 只监控第一个场次
        first_visit = visits[0]
        status = first_visit.get("availability", "")
        desc = first_visit.get("descrAvailability", "")
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        log = f"[{current_time}] 状态: {status} | {desc}"
        print(log)

        # 只要不是售罄，就发通知
        if status != "SOLD_OUT":
            wechat_notify("🚨 梵蒂冈门票有票啦！", log)

    except Exception as e:
        print(f"检查出错: {e}")

if __name__ == "__main__":
    check_tickets()
