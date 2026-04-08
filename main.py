import requests
import time

# ===================== 配置 =====================
VISITOR_NUM = 2
SENDKEY    = "SCT335071T4mVM8yeqsUYpyVOIZpZFjACJ"

# 监控日期
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
        requests.post(api, data={"title": title, "desc": content}, timeout=10)
    except:
        pass

# 检查单个日期
def check_date(VISIT_DATE):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n==============================================")
    print(f"[{now}] 正在检查：{VISIT_DATE}")

    try:
        # 1. 获取门票ID
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

        # 2. 获取时段
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

        # 打印时段（带日期）
        print(f"[{VISIT_DATE}] 各时段状态：")
        for item in timetable:
            print(f"[{VISIT_DATE}] {item['time']} -> {item['availability']}")

        # 判断是否有票
        has_ticket = any(t.get("availability") != "SOLD_OUT" for t in timetable)
        print(f"[{VISIT_DATE}] 最终结果：{'有票可预约' if has_ticket else '全部售罄'}")

        return has_ticket

    except Exception as e:
        print(f"[{VISIT_DATE}] 错误：{e}")
        return False

# 主程序
def main():
    available_list = []
    for date in MONITOR_DATES:
        if check_date(date):
            available_list.append(date)

    # 微信通知（带具体日期）
    if available_list:
        msg = "🚨 梵蒂冈门票可预约！\n"
        msg += f"人数：{VISITOR_NUM}\n\n"
        msg += "可预约日期：\n"
        for d in available_list:
            msg += f"✅ {d}\n"
        
        print(f"\n✅ 有可预约日期：{available_list}，发送微信通知")
        wechat_notify("🚨 梵蒂冈有票！", msg)

if __name__ == "__main__":
    main()
