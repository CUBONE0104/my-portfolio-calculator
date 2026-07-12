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
    {"級別": "N5", "單字": "學生", "假名": "がくせい", "詞性": "名詞", "中文意思": "學生", "例句": "私は学生です。", "例句假名": "わたしはがくせいです。", "例句中文": "我是學生。"},
    {"級別": "N5", "單字": "美味しい", "假名": "おいしい", "詞性": "形容詞", "中文意思": "美味的、好吃的", "例句": "このリンゴはとても美味しいです。", "例句假名": "このりんごはとてもおいしいです。", "例句中文": "這個蘋果非常好吃。"},
    {"級別": "N5", "單字": "行く", "假名": "いく", "詞性": "動詞", "中文意思": "去", "例句": "明日、日本へ行きます。", "例句假名": "あした、にほんへいきます。", "例句中文": "明天要去日本。"},
    {"級別": "N5", "單字": "飲む", "假名": "のむ", "詞性": "動詞", "中文意思": "喝", "例句": "コーヒーを飲みます。", "例句假名": "こーひーをのみます。", "例句中文": "喝咖啡。"},
    {"級別": "N4", "單字": "試驗", "假名": "しけん", "詞性": "名詞", "中文意思": "考試", "例句": "来週、日本語の試験があります。", "例句假名": "らいしゅう、にほんごのしけんがあります。", "例句中文": "下週有日文考試。"},
    {"級別": "N4", "單字": "集める", "假名": "あつめる", "詞性": "動詞", "中文意思": "收集、集中", "例句": "趣味はコインを集めることです。", "例句假名": "しゅみはこいんをあつめることです。", "例句中文": "我的興趣是收集硬幣。"},
    {"級別": "N4", "單字": "復習する", "假名": "ふくしゅうする", "詞性": "動詞", "中文意思": "複習", "例句": "レッスンをしっかりと復習します。", "例句假名": "れっすんをしっかりとふくしゅうします。", "例句中文": "好好複習課堂內容。"},
    {"級別": "N3", "單字": "準備", "假名": "じゅんび", "詞性": "名詞/動詞", "中文意思": "準備", "例句": "旅行の準備はもうできましたか。", "例句假名": "りょこうのじゅんびはもうできましたか。", "例句中文": "旅行的準備已經好了嗎？"},
    {"級別": "N3", "單字": "必ず", "假名": "かならず", "詞性": "副詞", "中文意思": "必定、務必", "例句": "約束は必ず守ります。", "例句假名": "やくそくはかならずまもります。", "例句中文": "約定好的事我一定會遵守。"},
    {"級別": "N3", "單字": "興味", "假名": "きょうみ", "詞性": "名詞", "中文意思": "興趣", "例句": "日本文化に興味があります。", "例句假名": "にほんぶんかにきょうみがあります。", "例句中文": "我對日本文化感興趣。"},
    {"級別": "N3", "單字": "解決する", "假名": "かいけつする", "詞性": "動詞", "中文意思": "解決", "例句": "問題を無事に解決しました。", "例句假名": "もんだいをぶじにかいけつしました。", "例句中文": "順利解決了問題。"}
]

def get_fixed_daily_words(date_seed_str):
    seed_num = int(date_seed_str.replace("-", ""))
    random.seed(seed_num)
    return random.sample(JAPANESE_WORDS, min(len(JAPANESE_WORDS), 5))

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

# =========================================================================
# 🔄 狀態初始化 (避免跨分頁數據干擾)
# =========================================================================
if "kara_list" not in st.session_state:
    st.session_state.kara_list = [
        {"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 70.0, "持有股數(股)": 4000},
        {"股號": "2330", "股票名稱": "台積電", "自訂產業備註": "半導體龍頭", "即時股價": 0.0, "原始總成本(萬元)": 25.0, "持有股數(股)": 350}
    ]
    st.session_state.kara_cash = 20.0
if "fish_list" not in st.session_state:
    st.session_state.fish_list = [{"股號": "00631L", "股票名稱": "元大台灣50正2", "自訂產業備註": "核心槓桿", "即時股價": 0.0, "原始總成本(萬元)": 30.0, "持有股數(股)": 1500}]
    st.session_state.fish_cash = 10.0

# 🎓 已學會單字列表（改用列表儲存，確保可以依序依時間由舊到新正序排列）
if "learned_history_list" not in st.session_state:
    st.session_state.learned_history_list = []

# 📝 小測驗換題核心回呼（完全解決測驗卡死問題）
def generate_new_quiz():
    st.session_state.quiz_item = random.choice(JAPANESE_WORDS)
    st.session_state.quiz_type = random.randint(0, 1)
    correct_word = st.session_state.quiz_item
    wrong_pool = [w for w in JAPANESE_WORDS if w["單字"] != correct_word["單字"]]
    wrong_choices = random.sample(wrong_pool, min(len(wrong_pool), 3))
    if st.session_state.quiz_type == 0:
        choices = [correct_word["假名"]] + [w["假名"] for w in wrong_choices]
    else:
        choices = [correct_word["單字"]] + [w["單字"] for w in wrong_choices]
    random.shuffle(choices)
    st.session_state.quiz_choices = choices
    st.session_state.quiz_submitted = False

# =========================================================================
# 🌐 左側主功能選單
# =========================================================================
page = st.sidebar.radio("🌐 選擇網頁功能", ["👦 卡拉的資產計算器", "👧 小魚的資產投資計算器", "🇯🇵 每日自動日文單字"])

# -------------------------------------------------------------------------
# 分頁三：🇯🇵 每日自動日文單字與測驗專區
# -------------------------------------------------------------------------
if page == "🇯🇵 每日自動日文單字":
    st.title("🇯🇵 N3-N5 智慧日文隨身卡與測驗")
    tab_study, tab_list, tab_quiz = st.tabs(["📥 歷史單字隨身卡", "🎓 已學會單字庫", "📝 挑戰日文小測驗"])

    with tab_study:
        selected_date = st.date_input("📅 選擇學習或複習的日期：", datetime.today())
        date_str = selected_date.strftime('%Y-%m-%d')
        st.write(f"目前顯示為 **{selected_date.strftime('%Y 年 %m 月 %d 日')}** 的精選單字卡。")
        st.write("---")

        daily_words = get_fixed_daily_words(date_str)

        for idx, item in enumerate(daily_words):
            unique_id = f"{date_str}_{item['單字']}"
            
            # 檢查目前清單中是否已經包含這顆字
            is_saved = any(x["id"] == unique_id for x in st.session_state.learned_history_list)

            if item["級別"] == "N3": st.error(f"日檢分級： {item['級別']} ")
            elif item["級別"] == "N4": st.warning(f"日檢分級： {item['級別']} ")
            else: st.success(f"日檢分級： {item['級別']} ")
            
            st.markdown(f"### 單字 {idx+1}：{item['單字']}（{item['詞性']}）")
            st.write(f"讀音假名：【 **{item['假名']}** 】")
            
            col_audio_ui, _ = st.columns(2)
            with col_audio_ui:
                word_audio = text_to_speech_bytes(item['單字'])
                if word_audio: st.audio(word_audio, format="audio/mp3")

            st.write(f"💡 **中文意思**： :blue[**{item['中文意思']}**]")
            st.write("📝 **實用例句：**")
            st.write(f"**{item['例句']}**")
            st.caption(f"（讀音：{item['例句假名']}）")
            st.write(f"➜ 中文：{item['例句中文']}")
            
            col_sentence_ui, _ = st.columns(2)
            with col_sentence_ui:
                sentence_audio = text_to_speech_bytes(item['例句'])
                if sentence_audio: st.audio(sentence_audio, format="audio/mp3")

            # 需求 4：互動打勾 (勾選加入，取消則動態剔除已學會區)
            state_checkbox = st.checkbox("💡 我已熟記學會此單字", value=is_saved, key=f"check_{unique_id}")
            
            if state_checkbox and not is_saved:
                st.session_state.learned_history_list.append({
                    "id": unique_id, "學習日期": date_str, "級別": item["級別"], "單字": item["單字"], "讀音": item["假名"], "意思": item["中文意思"]
                })
            elif not state_checkbox and is_saved:
                st.session_state.learned_history_list = [x for x in st.session_state.learned_history_list if x["id"] != unique_id]
                
            st.write("---")

    # 需求 1 & 2：已學會專區 (由舊到新正序、新增流水號編號、內建獨立移除按鈕)
    with tab_list:
        st.subheader("🎓 您的個人專屬熟記單字庫")
        if st.session_state.learned_history_list:
            st.write(f"恭喜！您與小魚目前累計已經背熟了 **{len(st.session_state.learned_history_list)}** 個單字！")
            
            # 從 session 列表中提取並轉換成 DataFrame
            df_learned = pd.DataFrame(st.session_state.learned_history_list)
            
            # 需求 2：對齊時間排列（由早到晚，第一個學會的在最上面，依序往下）
            df_learned = df_learned.sort_index(ascending=True)
            
            # 需求 2：將流水號強制設定為從 1 開始遞增
            df_learned.index = range(1, len(df_learned) + 1)
            
            # 表格美化重整呈現
            show_df = df_learned[["學習日期", "級別", "單字", "讀音", "意思"]]
            show_df.columns = ["出現日期", "日檢級別", "日文單字", "假名讀音", "中文意思"]
            st.dataframe(show_df, use_container_width=True)
            
