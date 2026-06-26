import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 網頁基本設定
st.set_page_config(page_title="雙人自訂資產計算器", layout="centered", page_icon="⚖️")

# 2. 共用即時股價與名稱查詢函式
@st.cache_data(ttl=600)  # 快取10分鐘，避免重複請求變慢
def get_taiwan_stock_info(symbol):
    """輸入股號（如 2330），自動去 yfinance 抓最新股價與官方名稱"""
    symbol = str(symbol).strip().upper()
    if not symbol:
        return 0.0, "請輸入股號"
    
    if not symbol.endswith(".TW"):
        symbol = f"{symbol}.TW"
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info['last_price']
        
        # 自動抓取股票官方名稱（如果抓不到就用股號代替）
        name = ticker.info.get('shortName', symbol)
        return round(price, 2), name
    except Exception:
        return 0.0, "查無此股號"

# 3. 初始化 session_state
if "kara_portfolio" not in st.session_state:
    st.session_state.kara_portfolio = pd.DataFrame([
        {"股號": "00631L", "自訂產業備註": "核心槓桿 / 台股正二", "原始總成本(萬元)": 70.0, "持有股數(股)": 4000},
        {"股號": "2330", "自訂產業備註": "晶圓代工 / 半導體龍頭", "原始總成本(萬元)": 25.0, "持有股數(股)": 350},
    ])
    st.session_state.kara_cash = 20.0
    st.session_state.kara_others_cost = 50.0
    st.session_state.kara_others_mv = 55.0

if "fish_portfolio" not in st.session_state:
    st.session_state.fish_portfolio = pd.DataFrame([
        {"股號": "00631L", "自訂產業備註": "核心槓桿", "原始總成本(萬元)": 30.0, "持有股數(股)": 1500},
        {"股號": "2330", "自訂產業備註": "半導體", "原始總成本(萬元)": 15.0, "持有股數(股)": 200},
    ])
    st.session_state.fish_cash = 10.0
    st.session_state.fish_others_cost = 20.0
    st.session_state.fish_others_mv = 25.0

# 4. 左側功能選單
page = st.sidebar.radio("🌐 選擇計算器主題", ["👦 卡拉的資產計算器", "👧 小魚寶寶的資產投資計算器"])

if page == "👦 卡拉的資產計算器":
    user_label = "卡拉"
    portfolio_key = "kara_portfolio"
    cash_key = "kara_cash"
    others_cost_key = "kara_others_cost"
    others_mv_key = "kara_others_mv"
else:
    user_label = "小魚"
    portfolio_key = "fish_portfolio"
    cash_key = "fish_cash"
    others_cost_key = "fish_others_cost"
    others_mv_key = "fish_others_mv"

st.title(f"{page}")
st.write("說明：在表格最下方點擊 **＋ Add row** 即可新增股票，輸入股號後系統會**自動帶入股票名稱**！")
st.write("---")

# 區塊一：基本資產
st.subheader("💵 基本資產配置")
col_base1, col_base2, col_base3 = st.columns(3)
with col_base1:
    st.session_state[cash_key] = st.number_input(f"{user_label} 的現金持有金額 (萬元)", min_value=0.0, value=st.session_state[cash_key], step=1.0)
with col_base2:
    st.session_state[others_cost_key] = st.number_input(f"其他 原始成本 (萬元)", min_value=0.0, value=st.session_state[others_cost_key], step=1.0)
with col_base3:
    st.session_state[others_mv_key] = st.number_input(f"其他 當前市值 (萬元)", min_value=0.0, value=st.session_state[others_mv_key], step=1.0)

st.write("---")

# 區塊二：動態編輯表格
st.subheader("📈 台股資產清單")

edited_df = st.data_editor(
    st.session_state[portfolio_key],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "股號": st.column_config.TextColumn("股號 (如: 2330)", help="輸入後系統會自動去抓名稱與股價"),
        "自訂產業備註": st.column_config.TextColumn("自訂產業備註 (例如: AI/半導體/高股息)"),
        "原始總成本(萬元)": st.column_config.NumberColumn("原始總成本 (萬)", min_value=0.0, format="%.2f"),
        "持有股數(股)": st.column_config.NumberColumn("持有股數 (股)", min_value=0, step=1)
    }
)
st.session_state[portfolio_key] = edited_df

# 核心聯網計算
if not edited_df.empty:
    with st.spinner("🔄 正在擷取最新股票名稱與即時股價..."):
        # 同時抓取股價與名稱
        info_list = [get_taiwan_stock_info(row["股號"]) for _, row in edited_df.iterrows()]
    
    # 拆分結果塞入表格
    edited_df["股票名稱"] = [info[1] for info in info_list]
    edited_df["即時股價"] = [info[0] for info in info_list]
    
    edited_df["當前市值(萬元)"] = (edited_df["持有股數(股)"] * edited_df["即時股價"]) / 10000
    edited_df["報酬率(%)"] = ((edited_df["當前市值(萬元)"] - edited_df["原始總成本(萬元)"]) / edited_df["原始總成本(萬元)"] * 100).fillna(0.0)
    
    def calc_exposure(row):
        symbol = str(row["股號"]).strip().upper()
        if "00631L" in symbol:
            return row["當前市值(萬元)"] * 2
        return row["當前市值(萬元)"]
        
    edited_df["實質曝險額(萬元)"] = edited_df.apply(calc_exposure, axis=1)

    stock_cost_total = edited_df["原始總成本(萬元)"].sum()
    stock_mv_total = edited_df["當前市值(萬元)"].sum()
    stock_exposure_total = edited_df["實質曝險額(萬元)"].sum()
else:
    stock_cost_total = 0.0
    stock_mv_total = 0.0
    stock_exposure_total = 0.0
    edited_df["股票名稱"] = []
    edited_df["即時股價"] = []
    edited_df["當前市值(萬元)"] = []
    edited_df["報酬率(%)"] = []

# 總計公式
total_cost = stock_cost_total + st.session_state[others_cost_key]
total_market_value = st.session_state[cash_key] + stock_mv_total + st.session_state[others_mv_key]
total_exposure = stock_exposure_total + st.session_state[others_mv_key]
exposure_ratio = (total_exposure / total_market_value) if total_market_value > 0 else 0.0

total_stock_profit = (stock_mv_total + st.session_state[others_mv_key]) - total_cost
total_roi = (total_stock_profit / total_cost * 100) if total_cost > 0 else 0.0

# 區塊三：明細報表輸出（包含自動帶入的股票名稱與自訂產業備註）
if not edited_df.empty:
    st.write("▼ **即時估算明細表 (內含自動股票名稱)**")
    show_df = edited_df[["股號", "股票名稱", "自訂產業備註", "即時股價", "當前市值(萬元)", "報酬率(%)"]]
    st.dataframe(show_df.style.format({"即時股價": "{:.2f}", "當前市值(萬元)": "{:.2f} 萬", "報酬率(%)": "{:+.2f}%"}), use_container_width=True)

# 區塊四：看板展示
st.write("---")
col1, col2 = st.columns(2)
with col1:
    st.metric("💰 當前總資產規模 (含現金)", f"{total_market_value:.2f} 萬元")
with col2:
    st.metric("🎯 實質曝險比率", f"{exposure_ratio:.3f} ({exposure_ratio*100:.1f}%)")

# 區塊五：健康度評估
st.write("---")
st.subheader("🔍 曝險健康度評估")
if 1.35 <= exposure_ratio <= 1.50:
    st.success(f"✅ 狀態安全：當前總曝險為 **{exposure_ratio:.2f}**，符合 1.35 - 1.50 黃金區間。")
elif exposure_ratio > 1.50:
    st.error(f"⚠️ 警訊：曝險過高！已超出上限 1.50。")
    suggested_reduce = total_exposure - (1.5 * total_market_value)
    st.info(f"💡 建議：可將系統中帶有槓桿(如00631L)的部位，獲利了結約 **{suggested_reduce/2:.1f} 萬元** 轉為現金。")
else:
    st.warning(f"ℹ️ 提示：目前總曝險低於 1.35，若有閒置資金可分批配置。")

# 區塊六：總看板
st.write("---")
st.subheader("🏆 綜合投資報酬率看板")
st.metric("💎 投資組合總帳面損益", f"{total_stock_profit:+.2f} 萬元", f"總整體投報率 {total_roi:+.2f}%")

