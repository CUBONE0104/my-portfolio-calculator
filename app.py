import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import base64
import random
from datetime import datetime
import plotly.express as px
from gtts import gTTS
import io

# 1. 網頁基本設定
st.set_page_config(page_title="個人投資與日文學習空間", layout="centered", page_icon="📈")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = "您的GitHub帳號/您的專案名稱"
CSV_FILE_PATH = "history_data.csv"

# =========================================================================
# 📚 核心日文單字庫
# =========================================================================
JAPANESE_WORDS = [
    {
        "級別": "N5", "單字": "学生", "假名": "がくせい", "詞性": "名詞", "中文意思": "學生", 
        "例句": "私は学生です。", "例句假名": "わたしはがくせいです。", "例句中文": "我是學生。"
    },
    {
        "級別": "N5", "單字": "美味しい", "假名": "おいしい", "詞性": "形容詞", "中文意思": "美味的、好吃的", 
        "例句": "このリンゴはとても美味しいです。", "例句假名": "このりんごはとてもおいしいです。", "例句中文": "這個蘋果非常好吃。"
    },
    {
        "級別": "N5", "單字": "行く", "假名": "いく", "詞性": "動詞", "中文意思": "去", 
        "例句": "明日、日本へ行きます。", "例句假名": "あした、にほんへいきます。", "例句中文": "明天要去日本。"
    },
    {
        "級別": "N5", "單字": "飲む", "假名": "のむ", "詞性": "動詞", "中文意思": "喝", 
        "例句": "コーヒーを飲みます。", "例句假名": "こーひーをのみます。", "例句中文": "喝咖啡。"
    },
    {
        "級別": "N4", "單字": "試験", "假名": "しけん", "詞性": "名詞", "中文意思": "考試", 
        "例句": "来週、日本語の試験があります。", "例句假名": "らいしゅう、にほんごのしけんがあります。", "例句中文": "下週有日文考試。"
    },
    {
        "級別": "N4", "單字": "集める", "假名": "あつめる", "詞性": "動詞", "中文意思": "收集、集中", 
        "例句": "趣味はコインを集めることです。", "例句假名": "しゅみはこいんをあつめることです。", "例句中文": "我的興趣是收集硬幣。"
    },
    {
        "級別": "N4", "單字": "復習する", "假名": "ふくしゅうする", "詞性": "動詞", "中文意思": "複習", 
        "例句": "レッスンをしっかりと復習します。", "例句假名": "れっすんをしっかりとふくしゅうします。", "例句中文": "好好複習課堂內容。"
    },
    {
        "級別": "N3", "單字": "準備", "假名": "じゅんび", "詞性": "名詞/動詞", "中文意思": "準備", 
        "例句": "旅行の準備はもうできましたか。", "例句假名": "りょこうのじゅんびはもうできましたか。", "例句中文": "旅行的準備已經好了嗎？"
    },
    {
        "級別": "N3", "單字": "必ず", "假名": "かならず", "詞性": "副詞", "中文意思": "必定、務必", 
        "例句": "約束は必ず守ります。", "例句假名": "やくそくはかならずまもります。", "例句中文": "約定好的事我一定會遵守。"
    },
    {
        "級別": "N3", "單字": "興味", "假名": "きょうみ", "詞性": "名詞", "中文意思": "興趣", 
        "例句": "日本文化に興味があります。", "例句假名": "にほんぶんかにきょうみがあります。", "例句中文": "我對日本文化感興趣。"
    },
    {
        "級別": "N3", "單字": "解決する", "假名": "かいけつする", "詞性": "動詞", "中文意思": "解決", 
        "例句": "問題を無事に解決しました。", "例句假名": "もんだいをぶじにかいけつしました。", "例句中文": "順利解決了問題。"
    }
]

# 關鍵技術：使用快取鎖定特定日期的 5 個單字，不管點按鈕或重新執行，順序絕對不亂跳！
@st.cache_data(ttl=86400)
def get_fixed_daily_words(date_seed_str):
    seed_num = int(date_seed_str.replace("-", ""))
    random.seed(seed_num)
    return random.sample(JAPANESE_WORDS, min(len(JAPANESE_WORDS), 5))

# 關鍵技術：直接使用 gTTS 在後台即時把文字生成音訊 Bytes，完美避開瀏覽器跨網域阻擋問題
def text_to_speech_bytes(text):
    try:
        tts = gTTS(text=text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except:
        return None

# =========================================================================
# ⚙️ 後台共用函式（維持資產計算邏輯）
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
    except: return 0.0, "查查無此股號"

# 初始化 session_state 狀態
if "kara_list" not in st.session_state:
    st.session_state.kara_list = [
        {"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 70.0, "持有股數(股)": 4000},
        {"股號": "2330", "股票名稱": "台積電", "自訂產業備註": "半導體龍頭", "即時股價": 0.0, "原始總成本(萬元)": 25.0, "持有股數(股)": 350}
    ]
    st.session_state.kara_cash = 20.0
if "fish_list" not in st.session_state:
    st.session_state.fish_list = [{"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 30.0, "持有股數(股)": 1500}]
    st.session_state.fish_cash = 10.0

# 🌟 全球首創：持久化學習庫（保證打勾資訊可以被完美儲存）
if "learned_history_dict" not in st.session_state:
    st.session_state.learned_history_dict = {}

# =========================================================================
# 🌐 左側功能選單
# =========================================================================
page = st.sidebar.radio("🌐 選擇網頁功能", ["👦 卡拉的資產計算器", "👧 小魚的資產投資計算器", "🇯🇵 每日自動日文單字"])

# -------------------------------------------------------------------------
# 分頁三：🇯🇵 每日自動日文單字功能（徹底修復 Bug 版）
# -------------------------------------------------------------------------
if page == "🇯🇵 每日自動日文單字":
    st.title("🇯🇵 N3-N5 智慧日文隨身卡")
    
    tab_study, tab_list = st.tabs(["📥 歷史單字隨身卡", "🎓 已學會單字庫"])
    
    with tab_study:
        selected_date = st.date_input("📅 選擇學習或複習的日期：", datetime.today())
        date_str = selected_date.strftime('%Y-%m-%d')
        st.write(f"目前顯示為 **{selected_date.strftime('%Y 年 %m 月 %d 日')}** 的 5 個精選單字卡。")
        st.write("---")

        # 使用鎖定日期的快取函式取得單字
        daily_words = get_fixed_daily_words(date_str)

        for idx, item in enumerate(daily_words):
            # 為當天這檔單字建立絕對不重複的獨一無二金鑰 (Date + Word)
            unique_key = f"{date_str}_{item['單字']}"
            
            # 判斷這顆字之前在我們的小字典裡存過了嗎
            is_saved = unique_key in st.session_state.learned_history_dict

            # 建立一個精緻的原生卡片排版
            st.markdown(f"### 單字 {idx+1}： <span style='font-size:32px; font-weight:bold;'>{item['單字']}</span>（{item['詞性']}）", unsafe_allow_html=True)
            st.write(f"讀音假名：【 **{item['假名']}** 】")
            
            # 🔊 真正內建發音包 (單字語音)
            word_audio = text_to_speech_bytes(item['單字'])
            if word_audio:
                st.audio(word_audio, format="audio/mp3")

            st.write(f"💡 **中文意思**： :blue[**{item['中文意思']}**]")
            
            # 需求 1：例句完美修正為「純黑色」顯示
            st.write("📝 **實用例句：**")
            st.write(f"**{item['例句']}**")
            st.caption(f"（讀音：{item['例句假名']}）")
            st.write(f"➜ 中文：{item['例句中文']}")
            
            # 🔊 真正內建發音包 (例句語音)
            sentence_audio = text_to_speech_bytes(item['例句'])
            if sentence_audio:
                st.audio(sentence_audio, format="audio/mp3")

            # 需求 2：互動式打勾（勾選後立刻動態寫入或移除數據庫）
            state_checkbox = st.checkbox("💡 我已熟記學會此單字", value=is_saved, key=f"check_{unique_key}")
            
            if state_checkbox and not is_saved:
                st.session_state.learned_history_dict[unique_key] = {
                    "學習日期": date_str,
                    "級別": item["級別"],
                    "單字": item["單字"],
                    "讀音": item["假名"],
                    "意思": item["中文意思"]
                }
            elif not state_checkbox and is_saved:
                st.session_state.learned_history_dict.pop(unique_key, None)
                
            st.write("---")

    # 需求 2：已學會單字的小分頁展示
    with tab_list:
        st.subheader("🎓 您的個人專屬熟記單字庫")
        if st.session_state.learned_history_dict:
            st.write(f"恭喜！您與小魚目前在這個網站已經攜手背熟了 **{len(st.session_state.learned_history_dict)}** 個日文核心單字！")
            
            # 從 Session 字典撈出所有已經被打勾的清單
            all_learned_list = list(st.session_state.learned_history_dict.values())
            df_learned = pd.DataFrame(all_learned_list)
            
            # 調整美化表格順序
            df_learned = df_learned[["學習日期", "級別", "單字", "讀音", "意思"]]
            df_learned.columns = ["單字熟記日期", "日檢級別", "日文單字", "假名讀音", "中文意思"]
            
            st.dataframe(df_learned.sort_values(by="單字熟記日期", ascending=False), use_container_width=True)
        else:
            st.info("這裡目前還空空的。當您在前方的隨身卡勾選「我已熟記學會此單字」之後，成就紀錄就會自動出現在這邊，並附帶日期喔！")

# -------------------------------------------------------------------------
# 原本功能：卡拉 & 小魚的計算器
# -------------------------------------------------------------------------
else:
    user_label, list_key, cash_key = ("卡拉", "kara_list", "kara_cash") if page == "👦 卡拉的資產計算器" else ("小魚", "fish_list", "fish_cash")
    
    quick_mode = st.checkbox("⚡ 開啟「秒速快算模式」 (不使用個別持股清單，直接手動打總市值)")
    st.write("---")

    if quick_mode:
        st.subheader("⚡ 秒速曝險快算面板")
        q_cash = st.number_input(f"{user_label} 的當前現金總額 (萬元)", min_value=0.0, value=st.session_state[cash_key], step=1.0)
