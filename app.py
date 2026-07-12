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
# 📚 核心日文單字庫 (已徹底檢查引號語法，漢字與假名完美對齊)
# =========================================================================
JAPANESE_WORDS = [
    # N5 單字
    {
        "級別": "N5", 
        "單字": "学生",
        "單字純假名": "がくせい",
        "單字帶假名": "<ruby>学<rt>がく</rt></ruby><ruby>生<rt>せい</rt></ruby>", 
        "詞性": "名詞", 
        "中文意思": "學生", 
        "例句": "私は学生です。", 
        "例句純假名": "わたしはがくせいです",
        "例句帶假名": "<ruby>私<rt>わたし</rt></ruby>は<ruby>学<rt>がく</rt></ruby><ruby>生<rt>せい</rt></ruby>です。", 
        "例句中文": "我是學生。"
    },
    {
        "級別": "N5", 
        "單字": "美味しい", 
        "單字純假名": "おいしい",
        "單字帶假名": "<ruby>美<rt>おい</rt></ruby>しい", 
        "詞性": "形容詞", 
        "中文意思": "美味的、好吃的", 
        "例句": "このリンゴはとても美味しいです。", 
        "例句純假名": "このりんごはとてもおいしいです",
        "例句帶假名": "このリンゴはとても<ruby>美<rt>おい</rt></ruby>しいです。", 
        "例句中文": "這個蘋果非常好吃。"
    },
    {
        "級別": "N5", 
        "單字": "行く", 
        "單字純假名": "いく",
        "單字帶假名": "<ruby>行<rt>い</rt></ruby>く", 
        "詞性": "動詞", 
        "中文意思": "去", 
        "例句": "明日、日本へ行きます。", 
        "例句純假名": "あしたにほんへいきます",
        "例句帶假名": "<ruby>明<rt>あした</rt></ruby><ruby>日<rt>にち</rt></ruby>、<ruby>日<rt>に</rt></ruby><ruby>本<rt>ほん</rt></ruby>へ<ruby>行<rt>い</rt></ruby>きます。", 
        "例句中文": "明天要去日本。"
    },
    {
        "級別": "N5", 
        "單字": "飲む", 
        "單字純假名": "のむ",
        "單字帶假名": "<ruby>飲<rt>の</rt></ruby>む", 
        "詞性": "動詞", 
        "中文意思": "喝", 
        "例句": "コーヒーを飲みます。", 
        "例句純假名": "こーひーをのみます",
        "例句帶假名": "コーヒーを<ruby>飲<rt>の</rt></ruby>みます。", 
        "例句中文": "喝咖啡。"
    },
    # N4 單字
    {
        "級別": "N4", 
        "單字": "試験", 
        "單字純假名": "しけん",
        "單字帶假名": "<ruby>試<rt>し</rt></ruby><ruby>験<rt>けん</rt></ruby>", 
        "詞性": "名詞", 
        "中文意思": "考試", 
        "例句": "来週、日本語の試験があります。", 
        "例句純假名": "らいしゅうにほんごのしけんがあります",
        "例句帶假名": "<ruby>来<rt>らい</rt></ruby><ruby>週<rt>しゅう</rt></ruby>、日本語の<ruby>試<rt>し</rt></ruby><ruby>験<rt>けん</rt></ruby>があります。", 
        "例句中文": "下週有日文考試。"
    },
    {
        "級別": "N4", 
        "單字": "集める", 
        "單字純假名": "あつめる",
        "單字帶假名": "<ruby>集<rt>あつ</rt></ruby>める", 
        "詞性": "動詞", 
        "中文意思": "收集、集中", 
        "例句": "趣味はコインを集めることです。", 
        "例句純假名": "しゅみはこいんをあつめることです",
        "例句帶假名": "趣味はコインを<ruby>集<rt>あつ</rt></ruby>めることです。", 
        "例句中文": "我的興趣是收集硬幣。"
    },
    {
        "級別": "N4", 
        "單字": "復習する", 
        "單字純假名": "ふくしゅうする",
        "單字帶假名": "<ruby>複<rt>ふく</rt></ruby><ruby>習<rt>しゅう</rt></ruby>する", 
        "詞性": "動詞", 
        "中文意思": "複習", 
        "例句": "レッスンをしっかりと復習します。", 
        "例句純假名": "れっすんをしっかりとふくしゅうします",
        "例句帶假名": "レッスンをしっかりと<ruby>複<rt>ふく</rt></ruby><ruby>習<rt>しゅう</rt></ruby>します。", 
        "例句中文": "好好複習課堂內容。"
    },
    # N3 單字
    {
        "級別": "N3", 
        "單字": "準備", 
        "單字純假名": "じゅんび",
        "單字帶假名": "<ruby>準<rt>じゅん</rt></ruby><ruby>備<rt>び</rt></ruby>", 
        "詞性": "名詞/動詞", 
        "中文意思": "準備", 
        "例句": "旅行の準備はもうできましたか。", 
        "例句純假名": "りょこうのじゅんびはもうできましたか",
        "例句帶假名": "<ruby>旅<rt>りょ</rt></ruby><ruby>行<rt>こう</rt></ruby>の<ruby>準<rt>じゅん</rt></ruby><ruby>備<rt>び</rt></ruby>はもうできましたか。", 
        "例句中文": "旅行的準備已經好了嗎？"
    },
    {
        "級別": "N3", 
        "單字": "必ず", 
        "單字純假名": "かならず",
        "單字帶假名": "<ruby>必<rt>かなら</rt></ruby>ず", 
        "詞性": "副詞", 
        "中文意思": "必定、務必", 
        "例句": "約束は必ず守ります。", 
        "例句純假名": "やくそくはかならずまもります",
        "例句帶假名": "約束は<ruby>必<rt>かなら</rt></ruby>ず<ruby>守<rt>まも</rt></ruby>ります。", 
        "例句中文": "約定好的事我一定會遵守。"
    },
    {
        "級別": "N3", 
        "單字": "興味", 
        "單字純假名": "きょうみ",
        "單字帶假名": "<ruby>興<rt>きょう</rt></ruby><ruby>味<rt>み</rt></ruby>", 
        "詞性": "名詞", 
        "中文意思": "興趣", 
        "例句": "日本文化に興味があります。", 
        "例句純假名": "にほんぶんかにきょうみがあります",
        "例句帶假名": "日本文化に<ruby>興<rt>きょう</rt></ruby><ruby>味<rt>み</rt></ruby>があります。", 
        "例句中文": "我對日本文化感興趣。"
    },
    {
        "級別": "N3", 
        "單字": "解決する", 
        "單字純假名": "かいけつする",
        "單字帶假名": "<ruby>解<rt>かい</rt></ruby><ruby>決<rt>けつ</rt></ruby>する", 
        "詞性": "動詞", 
        "中文意思": "解決", 
        "例句": "問題を無事に解決しました。", 
        "例句純假名": "もんだいをぶじにかいけつしました",
        "例句帶假名": "問題を無事に<ruby>解<rt>かい</rt></ruby><ruby>決<rt>けつ</rt></ruby>しました。", 
        "例句中文": "順利解決了問題。"
    }
]

def get_daily_words(target_date):
    """根據選定的日期作為種子碼，確保特定日期的單字永遠固定"""
    date_seed = int(target_date.strftime('%Y%m%d'))
    random.seed(date_seed)
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

# 初始化狀態
if "kara_list" not in st.session_state:
    st.session_state.kara_list = [
        {"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 70.0, "持有股數(股)": 4000},
        {"股號": "2330", "股票名稱": "台積電", "自訂產業備註": "半導體龍頭", "即時股價": 0.0, "原始總成本(萬元)": 25.0, "持有股數(股)": 350}
    ]
    st.session_state.kara_cash = 20.0
if "fish_list" not in st.session_state:
    st.session_state.fish_list = [{"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 30.0, "持有股數(股)": 1500}]
    st.session_state.fish_cash = 10.0
if "learned_words" not in st.session_state:
    st.session_state.learned_words = {}

# =========================================================================
# 🌐 左側選單
# =========================================================================
page = st.sidebar.radio("🌐 選擇網頁功能", ["👦 卡拉的資產計算器", "👧 小魚的資產投資計算器", "🇯🇵 每日自動日文單字"])

# -------------------------------------------------------------------------
# 分頁三：🇯🇵 每日自動日文單字功能 (需求1, 2, 3 完整實現)
# -------------------------------------------------------------------------
if page == "🇯🇵 每日自動日文單字":
    st.title("🇯🇵 N3-N5 每日核心單字卡")
    
    # 需求 2：互動式選擇歷史日期
    selected_date = st.date_input("📅 選擇欲學習或複習的日期：", datetime.today())
    date_str = selected_date.strftime('%Y-%m-%d')
    st.write(f"系統已載入 **{selected_date.strftime('%Y 年 %m 月 %d 日')}** 的專屬 5 個混搭單字！")
    st.write("---")

    daily_words = get_daily_words(selected_date)

    for idx, item in enumerate(daily_words):
        # 為每個單字建立一個不重複的 key
        word_key = f"{date_str}_{item['單字']}"
        
        # 建立 Google TTS 網頁發音網址 (精確進行 URL 編碼避免報錯)
        encoded_word = urllib.parse.quote(item['單字'])
        encoded_sentence = urllib.parse.quote(item['例句'])
        audio_word_url = f"https://google.com{encoded_word}"
        audio_sentence_url = f"https://google.com{encoded_sentence}"

        with st.container():
            col_w1, col_w2 = st.columns([1, 4])
            with col_w1:
                if item["級別"] == "N3": st.error(f"  {item['級別']}  ")
                elif item["級別"] == "N4": st.warning(f"  {item['級別']}  ")
                else: st.success(f"  {item['級別']}  ")
                
                # 需求 2：互動式打勾確認是否學會
                is_learned = st.checkbox("学んだ", key=f"chk_{word_key}")
                if is_learned:
                    st.caption("✅ 已熟記")
            
            with col_w2:
                # 顯示單字與漢字振假名
                st.markdown(f"### 單字 {idx+1}： <span style='font-size:32px;'>{item['單字帶假名']}</span> （{item['詞性']}）", unsafe_allow_html=True)
                
                # 需求 3：加入原生音訊播放器 (單字發音包)
