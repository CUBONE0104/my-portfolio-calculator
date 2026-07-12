import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import base64
import random
from datetime import datetime
import plotly.express as px
import urllib.parse

# 1. 網頁基本設定
st.set_page_config(page_title="個人投資與日文學習空間", layout="centered", page_icon="📈")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = "您的GitHub帳號/您的專案名稱"
CSV_FILE_PATH = "history_data.csv"

# =========================================================================
# 📚 核心日文單字庫 (乾淨的分離架構：純文字用於語音，HTML用於顯示)
# =========================================================================
JAPANESE_WORDS = [
    {
        "級別": "N5", 
        "單字純文字": "学生",
        "單字帶假名": "<ruby>学<rt>がく</rt></ruby><ruby>生<rt>せい</rt></ruby>", 
        "詞性": "名詞", 
        "中文意思": "學生", 
        "例句純文字": "私は学生です。", 
        "例句帶假名": "<ruby>私<rt>わたし</rt></ruby>は<ruby>学<rt>がく</rt></ruby><ruby>生<rt>せい</rt></ruby>です。", 
        "例句中文": "我是學生。"
    },
    {
        "級別": "N5", 
        "單字純文字": "美味しい", 
        "單字帶假名": "<ruby>美<rt>おい</rt></ruby>しい", 
        "詞性": "形容詞", 
        "中文意思": "美味的、好吃的", 
        "例句純文字": "このリンゴはとても美味しいです。", 
        "例句帶假名": "このリンゴはとても<ruby>美<rt>おい</rt></ruby>しいです。", 
        "例句中文": "這個蘋果非常好吃。"
    },
    {
        "級別": "N5", 
        "單字純文字": "行く", 
        "單字帶假名": "<ruby>行<rt>い</rt></ruby>く", 
        "詞性": "動詞", 
        "中文意思": "去", 
        "例句純文字": "明日、日本へ行きます。", 
        "例句帶假名": "<ruby>明<rt>あした</rt></ruby><ruby>日<rt>にち</rt></ruby>、<ruby>日<rt>に</rt></ruby><ruby>本<rt>ほん</rt></ruby>へ<ruby>行<rt>い</rt></ruby>きます。", 
        "例句中文": "明天要去日本。"
    },
    {
        "級別": "N5", 
        "單字純文字": "飲む", 
        "單字帶假名": "<ruby>飲<rt>の</rt></ruby>む", 
        "詞性": "動詞", 
        "中文意思": "喝", 
        "例句純文字": "コーヒーを飲みます。", 
        "例句帶假名": "コーヒーを<ruby>飲<rt>の</rt></ruby>みます。", 
        "例句中文": "喝咖啡。"
    },
    {
        "級別": "N4", 
        "單字純文字": "試験", 
        "單字帶假名": "<ruby>試<rt>し</rt></ruby><ruby>験<rt>けん</rt></ruby>", 
        "詞性": "名詞", 
        "中文意思": "考試", 
        "例句純文字": "来週、日本語の試験があります。", 
        "例句帶假名": "<ruby>来<rt>らい</rt></ruby><ruby>週<rt>しゅう</rt></ruby>、日本語の<ruby>試<rt>し</rt></ruby><ruby>験<rt>けん</rt></ruby>があります。", 
        "例句中文": "下週有日文考試。"
    },
    {
        "級別": "N4", 
        "單字純文字": "集める", 
        "單字帶假名": "<ruby>集<rt>あつ</rt></ruby>める", 
        "詞性": "動詞", 
        "中文意思": "收集、集中", 
        "例句純文字": "趣味はコインを集めることです。", 
        "例句帶假名": "趣味はコインを<ruby>集<rt>あつ</rt></ruby>めることです。", 
        "例句中文": "我的興趣是收集硬幣。"
    },
    {
        "級別": "N4", 
        "單字純文字": "復習する", 
        "單字帶假名": "<ruby>複<rt>ふく</rt></ruby><ruby>習<rt>しゅう</rt></ruby>する", 
        "詞性": "動詞", 
        "中文意思": "複習", 
        "例句純文字": "レッスンをしっかりと復習します。", 
        "例句帶假名": "レッスンをしっかりと<ruby>複<rt>ふく</rt></ruby><ruby>習<rt>しゅう</rt></ruby>します。", 
        "例句中文": "好好複習課堂內容。"
    },
    {
        "級別": "N3", 
        "單字純文字": "準備", 
        "單字帶假名": "<ruby>準<rt>じゅん</rt></ruby><ruby>備<rt>び</rt></ruby>", 
        "詞性": "名詞/動詞", 
        "中文意思": "準備", 
        "例句純文字": "旅行の準備はもうできましたか。", 
        "例句帶假名": "<ruby>旅<rt>りょ</rt></ruby><ruby>行<rt>こう</rt></ruby>の<ruby>準<rt>じゅん</rt></ruby><ruby>備<rt>び</rt></ruby>はもうできましたか。", 
        "例句中文": "旅行的準備已經好了嗎？"
    },
    {
        "級別": "N3", 
        "單字純文字": "必ず", 
        "單字帶假名": "<ruby>必<rt>かなら</rt></ruby>ず", 
        "詞性": "副詞", 
        "中文意思": "必定、務必", 
        "例句純文字": "約束は必ず守ります。", 
        "例句帶假名": "約束は<ruby>必<rt>かなら</rt></ruby>ず<ruby>守<rt>まも</rt></ruby>ります。", 
        "例句中文": "約定好的事我一定會遵守。"
    },
    {
        "級別": "N3", 
        "單字純文字": "興味", 
        "單字帶假名": "<ruby>興<rt>きょう</rt></ruby><ruby>味<rt>み</rt></ruby>", 
        "詞性": "名詞", 
        "中文意思": "興趣", 
        "例句純文字": "日本文化に興味があります。", 
        "例句帶假名": "日本文化に<ruby>興<rt>きょう</rt></ruby><ruby>味<rt>み</rt></ruby>があります。", 
        "例句中文": "我對日本文化感興趣。"
    },
    {
        "級別": "N3", 
        "單字純文字": "解決する", 
        "單字帶假名": "<ruby>解<rt>かい</rt></ruby><ruby>決<rt>けつ</rt></ruby>する", 
        "詞性": "動詞", 
        "中文意思": "解決", 
        "例句純文字": "問題を無事に解決しました。", 
        "例句帶假名": "問題を無事に<ruby>解<rt>かい</rt></ruby><ruby>決<rt>けつ</rt></ruby>しました。", 
        "例句中文": "順利解決了問題。"
    }
]

def get_daily_words(target_date):
    date_seed = int(target_date.strftime('%Y%m%d'))
    random.seed(date_seed)
    return random.sample(JAPANESE_WORDS, min(len(JAPANESE_WORDS), 5))

# =========================================================================
# ⚙️ 後台共用函式（維持投資理財核心計算）
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

# 初始化 session_state
if "kara_list" not in st.session_state:
    st.session_state.kara_list = [
        {"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 70.0, "持有股數(股)": 4000},
        {"股號": "2330", "股票名稱": "台積電", "自訂產業備註": "半導體龍頭", "即時股價": 0.0, "原始總成本(萬元)": 25.0, "持有股數(股)": 350}
    ]
    st.session_state.kara_cash = 20.0
if "fish_list" not in st.session_state:
    st.session_state.fish_list = [{"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 30.0, "持有股數(股)": 1500}]
    st.session_state.fish_cash = 10.0

# 🎓 核心功能：永久記錄已學會單字的字典
if "mastered_dictionary" not in st.session_state:
    st.session_state.mastered_dictionary = {}

# =========================================================================
# 🌐 左側功能選單
# =========================================================================
page = st.sidebar.radio("🌐 選擇網頁功能", ["👦 卡拉的資產計算器", "👧 小魚的資產投資計算器", "🇯🇵 每日自動日文單字"])

# -------------------------------------------------------------------------
# 分頁三：🇯🇵 每日自動日文單字功能 (全新修復＋新增已學會小分頁)
# -------------------------------------------------------------------------
if page == "🇯🇵 每日自動日文單字":
    st.title("🇯🇵 N3-N5 智慧日文學習庫")
    
    # 建立兩個小分頁
    tab_learn, tab_archive = st.tabs(["📥 歷史單字學習卡", "🎓 已學會單字庫"])
    
    with tab_learn:
        selected_date = st.date_input("📅 選擇欲學習的日期：", datetime.today())
        date_str = selected_date.strftime('%Y-%m-%d')
        st.write(f"系統已成功載入 **{selected_date.strftime('%Y-%m-%d')}** 的 5 個單字！")
        st.write("---")

        daily_words = get_daily_words(selected_date)

        for idx, item in enumerate(daily_words):
            unique_id = f"{date_str}_{item['單字純文字']}"
            
            # 【關鍵修復】語音包只讀取「純日文字串」，排除 HTML 標籤
            encoded_word = urllib.parse.quote(item['單字純文字'])
            encoded_sentence = urllib.parse.quote(item['例句純文字'])
            audio_word_url = f"https://google.com{encoded_word}"
            audio_sentence_url = f"https://google.com{encoded_sentence}"

            # 檢查這個單字之前有沒有被勾選過
            is_already_mastered = unique_id in st.session_state.mastered_dictionary

            with st.container():
                col_w1, col_w2 = st.columns([1, 4])
                with col_w1:
                    if item["級別"] == "N3": st.error(f"  {item['級別']}  ")
                    elif item["級別"] == "N4": st.warning(f"  {item['級別']}  ")
                    else: st.success(f"  {item['級別']}  ")
                    
                    # 互動式打勾
                    check_status = st.checkbox("學會了", value=is_already_mastered, key=f"chk_{unique_id}")
                    
                    # 狀態記憶邏輯：勾選就存入字典，取消勾選就移除
                    if check_status and not is_already_mastered:
                        st.session_state.mastered_dictionary[unique_id] = {
                            "單字": item["單字純文字"],
                            "級別": item["級別"],
                            "意思": item["中文意思"],
                            "發現日期": date_str
                        }
                    elif not check_status and is_already_mastered:
                        st.session_state.mastered_dictionary.pop(unique_id, None)

                with col_w2:
                    st.markdown(f"### 單字 {idx+1}： <span style='font-size:30px;'>{item['單字帶假名']}</span> （{item['詞性']}）", unsafe_allow_html=True)
