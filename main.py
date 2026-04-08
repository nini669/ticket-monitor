import requests
import time
from datetime import datetime, timedelta

# ===================== 配置 =====================
VISITOR_NUM = 2
SENDKEY    = "SCT335071T4mVM8yeqsUYpyVOIZpZFjACJ"

MONITOR_DATES = [  
    "18/04/2026",
    "20/04/2026"
]
# ==================================================

API_LIST = "https://tickets.museivaticani.va/api/search/resultPerTag"
API_TIME = "https://tickets.museivaticani.va/api/visit/timeavail"

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

def check_date(VISIT_DATE):
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n==============================================")
    print(f"[{beijing_time}] 检查：{VISIT_DATE}")

    try:
        params_list = {
            "lang": "it",
            "visitorNum": VISITOR_NUM,
            "visitDate": VISIT_DATE,
            "area": 1,
            "who": "",
            "page": 0,
            "tag": "MV-Biglietti"
        }
        r1 = requests.get(API_LIST, params=params_list, headers=HEADERS, timeout=15)
        data1 = r1.json()
        visits = data1.get("visits", [])
        if not visits:
            print(f"[{VISIT_DATE}] 无场次")
            return False

        visit_id = visits[0]["id"]
        print(f"[{VISIT_DATE}] 门票ID：{visit_id}")

        params_time = {
            "lang": "it",
            "visitLang": "",
            "visitTypeId": visit_id,
            "visitorNum": VISITOR_NUM,
            "visitDate": VISIT_DATE
        }
        r2 = requests.get(API_TIME, params=params_time, headers=HEADERS, timeout=15)
        data2 = r2.json()
        timetable = data2.get("timetable", [])

        # 打印时段
        print(f"[{VISIT_DATE}] 各时段状态：")
        for item in timetable:
            print(f"[{VISIT_DATE}] {item['time']} -> {item['availability']}")

        has_ticket = any(t.get("availability") != "SOLD_OUT" for t in timetable)
        result = "有票可预约" if has_ticket else "全部售罄"
        print(f"[{VISIT_DATE}] 最终结果：{result}")

        return has_ticket

    except Exception as e:
        print(f"[{VISIT_DATE}] 错误：{e}")
        return False

def main():
    available_dates = []
    for date in MONITOR_DATES:
        if check_date(date):
            available_dates.append(date)

    # ✅ 只在有票时发微信
    if available_dates:
        beijing_now = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        msg = f"🚨 梵蒂冈门票可预约！（北京时间 {beijing_now}）\n\n"
        msg += "可预约日期：\n"
        for d in available_dates:
            msg += f"✅ {d}\n"
        wechat_notify("🚨 梵蒂冈有票！", msg)

if __name__ == "__main__":
    main()
