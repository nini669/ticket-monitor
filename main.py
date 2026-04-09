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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win 64; x64) AppleWebKit/537.36",
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
        # ========== 第一层检查：列表接口（第一项状态）==========
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
            return False, "", False

        v0 = visits[0]
        visit_id = v0["id"]
        status = v0.get("availability", "")
        desc = v0.get("descrAvailability", "")
        print(f"[{VISIT_DATE}] 状态：{status}")

        # ========== 你要的第一层判断 ==========
        first_success = (status == "AVAILABLE") or (status != "SOLD_OUT")

        # ========== 第二层检查：时段接口 ==========
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
        print(f"[{VISIT_DATE}] 各时段：")
        for item in timetable:
            print(f" → {item['time']} : {item['availability']}")

        # 时段是否有可预约
        second_success = any(t.get("availability") != "SOLD_OUT" for t in timetable)

        # ========== 输出日志 ==========
        if first_success and second_success:
            print(f"✅ {VISIT_DATE}：有票 + 有时段")
        elif first_success:
            print(f"⚠️ {VISIT_DATE}：有票状态，但暂无时段")
        else:
            print(f"❌ {VISIT_DATE}：售罄")

        return first_success, desc, second_success

    except Exception as e:
        print(f"[{VISIT_DATE}] 错误：{e}")
        return False, "", False

def main():
    available_list = []
    beijing_now = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

    for date in MONITOR_DATES:
        first_ok, desc, second_ok = check_date(date)
        if first_ok:
            if second_ok:
                tip = "有时段可约"
            else:
                tip = "暂无时段可约"
            available_list.append((date, desc, tip))

    # ========== 只要第一层满足，就发微信 ==========
    if available_list:
        msg = f"🚨 梵蒂冈门票可预约！（北京时间 {beijing_now}）\n\n"
        msg += "可预约日期：\n"
        for d, desc, tip in available_list:
            msg += f"✅ {d}\n说明：{desc} {tip}\n\n"
        wechat_notify("🚨 梵蒂冈有票！", msg)

if __name__ == "__main__":
    main()

# ===================== 自动保持仓库活跃 =====================
import os
if os.path.exists("keep_alive.txt"):
    with open("keep_alive.txt", "w", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
# ============================================================
