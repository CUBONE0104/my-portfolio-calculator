import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import base64
import random
from datetime import datetime
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="個人投資與日文學習空間", layout="centered", page_icon="📈")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = "您的GitHub帳號/您的專案名稱"
CSV_FILE_PATH = "history_data.csv"

# =========================================================================
# 📚 核心日文單字庫 (隨機精選 N5-N3 常用單字，內建振假名 HTML 格式)
# =========================================================================
JAPANESE_WORDS = [
    # N5 單字
    {"級別": "N5", "單字": "<ruby>學<rt>まな</rt></r><ruby>生<rt>せい</rt></ruby>", "詞性": "名詞", "中文意思": "學生", "例句": "<ruby>私<rt>わたし</rt></ruby>は<ruby>學<rt>まな</rt></r><ruby>生<rt>せい</rt></ruby>です。", "例句中文": "我是學生。"},
    {"級別": "N5", "單字": "<ruby>美<rt>おい</rt></ruby>しい", "詞性": "形容詞", "中文意思": "美味的、好吃的", "例句":このリンゴはとても<ruby>美<rt>おい</rt></ruby>しいです。", "例句中文": "這個蘋果非常好吃。"},
    {"級別": "N5", "單字": "<ruby>行<rt>い</rt></ruby>く", "詞性": "動詞", "中文意思": "去", "例句": "<ruby>明<rt>あした</rt></ruby><ruby>日<rt>にち</rt></ruby>、<ruby>日<rt>に</rt></ruby><ruby>本<rt>ほん</rt></ruby>へ<ruby>行<rt>い</rt></ruby>きます。", "例句中文": "明天要去日本。"},
    # N4 單字
    {"級別": "N4", "單字": "<ruby>試<rt>し</rt></ruby><ruby>驗<rt>けん</rt></ruby>", "詞性": "名詞", "中文意思": "考試", "例句": "<ruby>來<rt>らい</rt></ruby><ruby>週<rt>しゅう</rt></ruby>、日本語の<ruby>試<rt>し</rt></ruby><ruby>驗<rt>けん</rt></ruby>があります。", "例句中文": "下週有日文考試。"},
    {"級別": "N4", "單字": "<ruby>集<rt>あつ</rt></ruby>める", "詞性": "動詞", "中文意思": "收集、集中", "例句":趣味はコインを<ruby>集<rt>あつ</rt></ruby>めることです。", "例句中文": "我的興趣是收集硬幣。"},
    {"級別": "N4", "單字": "<ruby>複<rt>ふく</rt></ruby><ruby>習<rt>しゅう</rt></ruby>する", "詞性": "動詞", "中文意思": "複習", "例句":レッスンをしっかりと<ruby>複<rt>ふく</rt></ruby><ruby>習<rt>しゅう</rt></ruby>します。", "例句中文": "好好複習課堂內容。"},
    # N3 單字
    {"級別": "N3", "單字": "<ruby>準<rt>じゅん</rt></ruby><ruby>備<rt>び</rt></ruby>", "詞性": "名詞/動詞", "中文意思": "準備", "例句": "<ruby>旅<rt>りょ</rt></ruby><ruby>行<rt>こう</rt></ruby>の<ruby>準<rt>じゅん</rt></ruby><ruby>備<rt>び</rt></ruby>はもうできましたか。", "例句中文": "旅行的準備已經好了嗎？"},
    {"級別": "N3", "單字": "<ruby>必<rt>かなら</rt></ruby>ず", "詞性": "副詞", "中文意思": "必定、務必", "例句":約束は<ruby>必<rt>かなら</rt></ruby>ず<ruby>守<rt>まも</rt></ruby>ります。", "例句中文": "約定好的事我一定會遵守。"},
    {"級別": "N3", "單字": "<ruby>興<rt>きょう</rt></ruby><ruby>味<rt>み</rt></ruby>", "詞性": "名詞", "中文意思": "興趣", "例句":日本文化に<ruby>興<rt>きょう</rt></ruby><ruby>味<rt>み</rt></ruby>があります。", "例句中文": "我對日本文化感興趣。"},
    {"級別": "N3", "單字": "<ruby>解<rt>かい</rt></ruby><ruby>決<rt>けつ</rt></ruby>する", "詞性": "動詞", "中文意思": "解決", "例句":問題を無事に<ruby>解<rt>かい</rt></ruby><ruby>決<rt>けつ</rt></ruby>しました。", "例句中文": "順利解決了問題。"},
    {"級別": "N5", "單字": "<ruby>飲<rt>の</rt></ruby>む", "詞性": "動詞", "中文意思": "喝", "例句":コーヒーを<ruby>飲<rt>の</rt></ruby>みます。", "例句中文": "喝咖啡。"}
]

def get_daily_words():
    """根據今天的日期作為種子碼，每天固定隨機抓取 5 個單字"""
    today_str = datetime.today().strftime('%Y%m%d')
    random.seed(int(today_str)) # 鎖定當天種子，確保整天刷新網頁都是同一批單字
    return random.sample(JAPANESE_WORDS, min(len(JAPANESE_WORDS), 5))

# =========================================================================
# ⚙️ 後台共用函式（維持您原有的 GitHub 歷史紀錄與股價查詢）
# =========================================================================
def save_to_github_csv(user, total_assets, profit, exposure_rate):
    if not GITHUB_TOKEN or "您的GitHub帳號" in REPO_NAME: return
    url = f"https://github.com{REPO_NAME}/contents/{CSV_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    today = datetime.today().strftime('%Y-%m-%d')
    new_row = f"\n{today},{user},{total_assets},{profit},{exposure_rate}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        file_data = res.json()
        sha = file_data["sha"]
        old_content = base64.b64decode(file_data["content"]).decode("utf-8")
        if today in old_content and user in old_content: return
        updated_content = old_content + new_row
    else:
        sha = None
        updated_content = "日期,使用者,總資產(萬),今日損益(萬),曝險比率(%)\n" + f"{today},{user},{total_assets},{profit},{exposure_rate}"
    payload = {"message": f"🤖 系統自動更新 {user} 每日資產紀錄", "content": base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")}
    if sha: payload["sha"] = sha
    requests.put(url, headers=headers, json=payload)

def load_history_data():
    url = f"https://githubusercontent.com{REPO_NAME}/main/{CSV_FILE_PATH}"
    try: return pd.read_csv(url)
    except:
        return pd.DataFrame({
            "日期": ["2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25", "2026-06-26"],
            "使用者": ["卡拉", "卡拉", "卡拉", "卡拉", "卡拉"],
            "總資產(萬)": [150.0, 152.5, 149.0, 155.2, 160.0],
            "今日損益(萬)": [0.0, 2.5, -3.5, 6.2, 4.8],
            "曝險比率(%)": [1.41, 1.43, 1.38, 1.45, 1.42]
        })

@st.cache_data(ttl=600)
def get_taiwan_stock_info(symbol):
    symbol = str(symbol).strip().upper()
    if not symbol: return 0.0, "請輸入股號"
    if not symbol.endswith(".TW"): symbol = f"{symbol}.TW"
    try:
        ticker = yf.Ticker(symbol)
        return round(ticker.fast_info['last_price'], 2), ticker.info.get('shortName', symbol)
    except: return 0.0, "查無此股號"

# 初始化持股狀態
if "kara_list" not in st.session_state:
    st.session_state.kara_list = [
        {"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 70.0, "持有股數(股)": 4000},
        {"股號": "2330", "股票名稱": "台積電", "自訂產業備註": "半導體龍頭", "即時股價": 0.0, "原始總成本(萬元)": 25.0, "持有股數(股)": 350}
    ]
    st.session_state.kara_cash = 20.0
if "fish_list" not in st.session_state:
    st.session_state.fish_list = [{"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 30.0, "持有股數(股)": 1500}]
    st.session_state.fish_cash = 10.0

# =========================================================================
# 🌐 左側選單 (加入日文分頁)
# =========================================================================
page = st.sidebar.radio("🌐 選擇網頁功能", ["👦 卡拉的資產計算器", "👧 小魚的資產投資計算器", "🇯🇵 每日自動日文單字"])

# -------------------------------------------------------------------------
# 分頁三：🇯🇵 每日自動日文單字功能
# -------------------------------------------------------------------------
if page == "🇯🇵 每日自動日文單字":
    st.title("🇯🇵 N3-N5 每日核心單字卡")
    today_date = datetime.today().strftime('%Y 年 %m 月 %d 日')
    st.write(f"今天是 **{today_date}**。系統已為您自動生成今日份的 5 個混搭單字！")
    st.write("---")

    daily_words = get_daily_words()

    for idx, item in enumerate(daily_words):
        # 使用 st.container 做出卡片外觀
        with st.container():
            col_w1, col_w2 = st.columns([1, 4])
            with col_w1:
                # 根據不同級別標上不同顏色標籤
                if item["級別"] == "N3": st.error(f"  {item['級別']}  ")
                elif item["級別"] == "N4": st.warning(f"  {item['級別']}  ")
                else: st.success(f"  {item['級別']}  ")
            with col_w2:
                # 核心：使用 HTML 輸出帶有漢字上方振假名的精美外觀
                st.markdown(f"### 單字 {idx+1}： <span style='font-size:32px;'>{item['單字']}</span> （{item['詞性']}）", unsafe_allow_html=True)
                st.markdown(f"💡 **中文意思**：<span style='color:#1E88E5; font-weight:bold;'>{item['中文意思']}</span>", unsafe_allow_html=True)
                st.write(f"📝 **實用例句**：")
                st.markdown(f"<p style='font-size:20px; background-color:#F0F2F6; padding:10px; border-radius:5px;'>{item['例句']}<br><span style='font-size:14px; color:#555;'>➜ {item['例句中文']}</span></p>", unsafe_allow_html=True)
        st.write("---")
    
    st.info("💡 溫馨提示：單字會於每日凌晨 00:00 自動更換，明天記得再來複習喔！")

# -------------------------------------------------------------------------
# 原本功能：卡拉 & 小魚的計算器（代碼維持不變，僅做整合）
# -------------------------------------------------------------------------
else:
    user_label, list_key, cash_key = ("卡拉", "kara_list", "kara_cash") if page == "👦 卡拉的資產計算器" else ("小魚", "fish_list", "fish_cash")
    
    quick_mode = st.checkbox("⚡ 開啟「秒速快算模式」 (不使用個別持股清單，直接手動打總市值)")
    st.write("---")

    if quick_mode:
        st.subheader("⚡ 秒速曝險快算面板")
        q_cash = st.number_input(f"{user_label} 的當前現金總額 (萬元)", min_value=0.0, value=st.session_state[cash_key], step=1.0)
        q_00631l = st.number_input("🚀 00631L 當前總市值 (萬元)", min_value=0.0, value=90.0, step=1.0)
        q_others = st.number_input("📈 其他所有股票 當前總市值 (萬元)", min_value=0.0, value=55.0, step=1.0)
        
        total_market_value = q_cash + q_00631l + q_others
        stock_exposure_total = (q_00631l * 2) + q_others
        exposure_ratio = (stock_exposure_total / total_market_value) if total_market_value > 0 else 0.0
        total_stock_profit = 0.0
        total_roi = 0.0
    else:
        st.subheader("💵 現金資產配置")
        st.session_state[cash_key] = st.number_input(f"{user_label} 的當前現金持有金額 (萬元)", min_value=0.0, value=st.session_state[cash_key], step=1.0)
        st.write("---")

        st.subheader("➕ 新增台股部位")
        col_in1, col_in2 = st.columns(2)
        with col_in1: input_symbol = st.text_input("第一步：請輸入台股股號 (如: 2330)", key=f"sym_{user_label}")
        with col_in2: check_btn = st.button("🔍 查詢股票資訊", key=f"btn_{user_label}")

        if input_symbol:
            current_price, official_name = get_taiwan_stock_info(input_symbol)
            if current_price > 0:
                st.success(f"📈 成功尋獲股票！【{official_name}】 | 目前即時股價：{current_price} 元")
                col_in3, col_in4, col_in5 = st.columns(3)
                with col_in3: input_shares = st.number_input("第二步：輸入持有股數 (股)", min_value=0, value=1000, step=100)
                with col_in4: input_cost = st.number_input("第三步：輸入原始總成本 (萬元)", min_value=0.0, value=10.0, step=1.0)
                with col_in5: input_note = st.text_input("第四步：自訂產業備註", value="AI/半導體")
                    
                if st.button("🚀 確認新增至資產清單", use_container_width=True):
                    st.session_state[list_key].append({"股號": input_symbol, "股票名稱": official_name, "自訂產業備註": input_note, "即時股價": current_price, "原始總成本(萬元)": input_cost, "持有股數(股)": input_shares})
