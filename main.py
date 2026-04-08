import requests
import time

# 配置
VISIT_DATE = "21/04/2026"
SENDKEY    = "SCT335071T4mVM8yeqsUYpyVOIZpZFjACJ"

# 正确的API（你截图里的resultPerTag接口）
URL = (
    "https://tickets.museivaticani.va/api/search/resultPerTag"
    f"?lang=it&visitorNum=2&visitDate={VISIT_DATE}&area=1&who=&page=0&tag=MV-Biglietti"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Referer": "https://tickets.museivaticani.va/",
    "Accept-Language": "it-IT,it;q=0.9"
}

def wechat_notify(title, content):
    try:
        api = f"https://sctapi.ftqq.com/{SENDKEY}.send"
        requests.post(api, data={"title": title, "desp": content}, timeout=10)
    except Exception as e:
        print(f"微信通知失败: {e}")

def main():
    try:
        r = requests.get(URL, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"请求失败，状态码: {r.status_code}")
            return

        data = r.json()
        visits = data.get("visits", [])
        if not visits:
            print("无场次")
            return

        # 只监控第一个场次
        v0 = visits[0]
        status = v0.get("availability")
        name = v0.get("name")
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        msg = f"[{now}]\n日期: {VISIT_DATE}\n票种: {name}\n状态: {status}"
        print(msg)

        # 核心判断：状态为AVAILABLE就报警
        if status == "AVAILABLE":
            wechat_notify("🚨 梵蒂冈4月21日门票可预订！", msg)

    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
