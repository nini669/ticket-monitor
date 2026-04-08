import requests
import time

# ===================== 配置 =====================
VISIT_DATE = "21/04/2026"
VISITOR_NUM = 2
SENDKEY    = "SCT335071T4ymVM8yeqsUYpyVOIZpZFjACJ"
# ==================================================

# 接口1：获取门票ID
API_LIST = (
    "https://tickets.museivaticani.va/api/search/resultPerTag"
    f"?lang=it&visitorNum={VISITOR_NUM}&visitDate={VISIT_DATE}&area=1&who=&page=0&tag=MV-Biglietti"
)

# 接口2：查询时段是否可约
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

def main():
    try:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"【{now}】开始检查梵蒂冈门票...")

        # 1. 获取场次ID
        r1 = requests.get(API_LIST, headers=HEADERS, timeout=15)
        data1 = r1.json()
        visits = data1.get("visits", [])
        if not visits:
            print("无场次信息")
            return

        visit_id = visits[0]["id"]
        print(f"获取门票ID成功: {visit_id}")

        # 2. 获取时间段可用性
        params = {
            "lang": "it",
            "visitLang": "",
            "visitTypeId": visit_id,
            "visitorNum": VISITOR_NUM,
            "visitDate": VISIT_DATE
        }
        r2 = requests.get(API_TIME, params=params, headers=HEADERS, timeout=15)
        data2 = r2.json()
        timetable = data2.get("timetable", [])

        # 打印所有时段结果
        print("\n==== 各时段状态 ====")
        for item in timetable:
            print(f"{item['time']} -> {item['availability']}")

        # 判断：任意时段不是SOLD_OUT就算有票
        has_ticket = any(t.get("availability") != "SOLD_OUT" for t in timetable)
        print(f"\n最终结果：{'有票可预约' if has_ticket else '全部售罄'}")

        # 有票才发微信（无任何测试消息）
        if has_ticket:
            msg = f"✅ 梵蒂冈 {VISIT_DATE} 有票！\n人数：{VISITOR_NUM}\n状态：可预约"
            wechat_notify("🚨 梵蒂冈门票可预约！", msg)

    except Exception as e:
        print(f"运行错误: {e}")

if __name__ == "__main__":
    main()
