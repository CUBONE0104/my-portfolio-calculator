import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import base64
from datetime import datetime
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="雙人資產與每日損益追蹤", layout="centered", page_icon="📈")

# 2. GitHub CSV 歷史數據同步設定 (用於每日損益折線圖)
# 提示：為了安全，您可以將 Token 設定在 Streamlit 雲端後台的 Secrets 中，這裡預設讀取環境變數
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "") # 請在 Streamlit 後台 Secrets 設定
REPO_NAME = "您的GitHub帳號/您的專案名稱" # 範例: "kara/my-invest-app"
CSV_FILE_PATH = "history_data.csv"

def save_to_github_csv(user, total_assets, profit, exposure_rate):
    """將每日數據自動存回 GitHub 的 CSV 檔案中"""
    if not GITHUB_TOKEN or "您的GitHub帳號" in REPO_NAME:
        return  # 若未設定則跳過（只在本地運行）
    
    url = f"https://github.com{REPO_NAME}/contents/{CSV_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    today = datetime.today().strftime('%Y-%m-%d')
    new_row = f"\n{today},{user},{total_assets},{profit},{exposure_rate}"
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        file_data = res.json()
        sha = file_data["sha"]
        old_content = base64.b64decode(file_data["content"]).decode("utf-8")
        if today in old_content and user in old_content:
            return # 今天已經紀錄過了
        updated_content = old_content + new_row
    else:
        sha = None
        updated_content = "日期,使用者,總資產(萬),今日損益(萬),曝險比率(%)\n" + f"{today},{user},{total_assets},{profit},{exposure_rate}"
        
    payload = {
        "message": f"🤖 系統自動更新 {user} 每日資產紀錄",
        "content": base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")
    }
    if sha: payload["sha"] = sha
    requests.put(url, headers=headers, json=payload)

def load_history_data():
    """從 GitHub 讀取歷史數據，若沒有則生成模擬數據供體驗折線圖"""
    url = f"https://githubusercontent.com{REPO_NAME}/main/{CSV_FILE_PATH}"
    try:
        df = pd.read_csv(url)
        return df
    except:
        # 預設模擬數據，讓您一上線就能看到折線圖長什麼樣子
        return pd.DataFrame({
            "日期": ["2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25", "2026-06-26"],
            "使用者": ["卡拉", "卡拉", "卡拉", "卡拉", "卡拉"],
            "總資產(萬)": [150.0, 152.5, 149.0, 155.2, 160.0],
            "今日損益(萬)": [0.0, 2.5, -3.5, 6.2, 4.8],
            "曝險比率(%)": [1.41, 1.43, 1.38, 1.45, 1.42]
        })

# 3. 共用即時股價與名稱查詢
@st.cache_data(ttl=600)
def get_taiwan_stock_info(symbol):
    symbol = str(symbol).strip().upper()
    if not symbol: return 0.0, "請輸入股號"
    if not symbol.endswith(".TW"): symbol = f"{symbol}.TW"
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info['last_price']
        name = ticker.info.get('shortName', symbol)
        return round(price, 2), name
    except:
        return 0.0, "查無此股號"

# 4. 初始化 session_state
if "kara_list" not in st.session_state:
    st.session_state.kara_list = [
        {"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 70.0, "持有股數(股)": 4000},
        {"股號": "2330", "股票名稱": "台積電", "自訂產業備註": "半導體龍頭", "即時股價": 0.0, "原始總成本(萬元)": 25.0, "持有股數(股)": 350}
    ]
    st.session_state.kara_cash = 20.0

if "fish_list" not in st.session_state:
    st.session_state.fish_list = [
        {"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 30.0, "持有股數(股)": 1500}
    ]
    st.session_state.fish_cash = 10.0

# 5. 左側功能選單
page = st.sidebar.radio("🌐 選擇計算器主題", ["👦 卡拉的資產計算器", "👧 小魚的資產投資計算器"])

if page == "👦 卡拉的資產計算器":
    user_label, list_key, cash_key = "卡拉", "kara_list", "kara_cash"
else:
    user_label, list_key, cash_key = "小魚", "fish_list", "fish_cash"

st.title(f"{page}")

# 需求 1：基本資產配置只留下現金
st.subheader("💵 現金資產配置")
st.session_state[cash_key] = st.number_input(f"{user_label} 的當前現金持有金額 (萬元)", min_value=0.0, value=st.session_state[cash_key], step=1.0)

st.write("---")

# 需求 2：分步輸入流程 (輸入股號 -> 按輸入 -> 帶出名稱股價 -> 輸入股數/成本 -> 確認新增)
st.subheader("➕ 新增台股部位")
col_in1, col_in2 = st.columns([2, 1])
with col_in1:
    input_symbol = st.text_input("第一步：請輸入台股股號 (如: 2330, 0050)", key=f"sym_{user_label}")
with col_in2:
    check_btn = st.button("🔍 查詢股票資訊", key=f"btn_{user_label}")

# 當使用者輸入股號並點擊查詢時
if input_symbol:
    current_price, official_name = get_taiwan_stock_info(input_symbol)
    if current_price > 0:
        st.success(f"📈 成功尋獲股票！【{official_name}】 | 目前即時股價：{current_price} 元")
        
        # 顯示第二步輸入框
        col_in3, col_in4, col_in5 = st.columns(3)
        with col_in3:
            input_shares = st.number_input("第二步：輸入持有股數 (股)", min_value=0, value=1000, step=100)
        with col_in4:
            input_cost = st.number_input("第三步：輸入原始總成本 (萬元)", min_value=0.0, value=10.0, step=1.0)
        with col_in5:
            input_note = st.text_input("第四步：自訂產業備註", value="AI/半導體/高股息")
            
        if st.button("🚀 確認新增至資產清單", use_container_width=True):
            # 將新股票塞入清單
            st.session_state[list_key].append({
                "股號": input_symbol,
                "股票名稱": official_name,
                "自訂產業備註": input_note,
                "即時股價": current_price,
                "原始總成本(萬元)": input_cost,
                "持有股數(股)": input_shares
            })
            st.toast(f"✅ 已成功將 {official_name} 加入您的資產清單！")
            st.rerun()
    else:
        st.error("❌ 找不到該股號，請確認數字是否輸入正確。")

st.write("---")

# 區塊三：重新計算與明細呈現
st.subheader("📋 當前持股明細表")
current_list = st.session_state[list_key]

if current_list:
    # 即時更新每檔股票的最新價格與市值
    updated_rows = []
    for row in current_list:
        p, n = get_taiwan_stock_info(row["股號"])
        row["即時股價"] = p
        row["當前市值(萬元)"] = round((row["持有股數(股)"] * p) / 10000, 2)
        row["報酬率(%)"] = round(((row["當前市值(萬元)"] - row["原始總成本(萬元)"]) / row["原始總成本(萬元)"] * 100), 2) if row["原始總成本(萬元)"] > 0 else 0.0
        row["實質曝險額(萬元)"] = row["當前市值(萬元)"] * 2 if "00631L" in str(row["股號"]).upper() else row["當前市值(萬元)"]
        updated_rows.append(row)
        
    df_display = pd.DataFrame(updated_rows)
    
    # 提供刪除功能
    st.write("💡 提示：若要刪除特定持股，可在下方勾選後點擊刪除。")
    del_list = []
    for i, r in df_display.iterrows():
        if st.checkbox(f"刪除 {r['股票名稱']} ({r['股號']})", key=f"del_{user_label}_{i}"):
            del_list.append(i)
            
    if del_list and st.button("🗑️ 執行刪除選中股票"):
        st.session_state[list_key] = [item for idx, item in enumerate(current_list) if idx not in del_list]
        st.rerun()

    # 顯示精美明細表
    st.dataframe(df_display[["股號", "股票名稱", "自訂產業備註", "即時股價", "當前市值(萬元)", "報酬率(%)"]], use_container_width=True)
    
    # 加總計算
    stock_cost_total = df_display["原始總成本(萬元)"].sum()
    stock_mv_total = df_display["當前市值(萬元)"].sum()
    stock_exposure_total = df_display["實質曝險額(萬元)"].sum()
else:
    st.info("目前清單空空如也，請在上方新增股票部位！")
    stock_cost_total, stock_mv_total, stock_exposure_total = 0.0, 0.0, 0.0

# 總資產與曝險公式
total_cost = stock_cost_total
total_market_value = st.session_state[cash_key] + stock_mv_total
exposure_ratio = (stock_exposure_total / total_market_value) if total_market_value > 0 else 0.0
total_stock_profit = stock_mv_total - total_cost
total_roi = (total_stock_profit / total_cost * 100) if total_cost > 0 else 0.0

# 顯示核心資產數據看板
st.write("---")
col1, col2 = st.columns(2)
with col1:
    st.metric("💰 當前總資產規模 (含現金)", f"{total_market_value:.2f} 萬元")
with col2:
    st.metric("🎯 實質曝險比率", f"{exposure_ratio:.3f} ({exposure_ratio*100:.1f}%)")

st.metric("🏆 投資組合總帳面損益", f"{total_stock_profit:+.2f} 萬元", f"總整體投報率 {total_roi:+.2f}%")

# 自動秘密存檔至 GitHub（如果帳號已綁定）
save_to_github_csv(user_label, total_market_value, total_stock_profit, exposure_ratio)

# 需求 3：每日損益、總資產、曝險 對時間的折線圖
st.write("---")
st.subheader("📈 歷史趨勢追蹤 (資產、損益與曝險)")

history_df = load_history_data()
# 篩選出目前選定使用者的數據
user_history = history_df[history_df["使用者"] == user_label].sort_values(by="日期")

if not user_history.empty:
    tab1, tab2, tab3 = st.tabs(["💵 總資產走勢", "📊 每日損益變動", "🎯 曝險比率追蹤"])
    
    with tab1:
        fig1 = px.line(user_history, x="日期", y="總資產(萬)", title=f"{user_label} 的總資產隨時間變化（萬元）", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        
    with tab2:
        fig2 = px.bar(user_history, x="日期", y="今日損益(萬)", title=f"{user_label} 的每日損益變動（萬元）", color="今日損益(萬)", color_continuous_scale=["red", "green"])
        st.plotly_chart(fig2, use_container_width=True)
        
    with tab3:
        fig3 = px.line(user_history, x="日期", y="曝險比率(%)", title=f"{user_label} 的實質曝險比率走勢", markers=True)
        st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("尚無歷史趨勢數據，當您設定好 GitHub 儲存功能後，系統每天會自動繪製圖表。")
