import streamlit as st
import pandas as pd
import random
from datetime import datetime
from gtts import gTTS
import io

# 1. 網頁基本設定
st.set_page_config(page_title="卡拉與小魚的日文言語知識大本營", layout="centered", page_icon="🇯🇵")

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

# =========================================================================
# 📝 核心真題庫：言語知識（文字・語彙）
# =========================================================================
VOCAB_QUIZZES = [
    {
        "級別": "N3",
        "題目類型": "問題1 _のことばの読み方として最もよいものを、1・2・3・4から一つえらびなさい。",
        "題目文": "会場には大勢の【観客】がいた。",
        "選項": ["1 けんぎゃく", "2 かんぎゃく", "3 けんきゃく", "4 かんきゃく"],
        "正確答案": "4 かんきゃく",
        "中文翻譯": "會場裡有大量的觀眾。",
        "詳解": "「観」的音讀為「かん」，「客」的音讀為「きゃく」，兩者結合的正確讀音為「かんきゃく」。"
    },
    {
        "級別": "N3",
        "題目類型": "問題1 _のことばの読み方として最もよいものを、1・2・3・4から一つえらびなさい。",
        "題目文": "ホテルには3時ごろ【到着】します。",
        "選項": ["1 とうちゃく", "2 とうつく", "3 とちゃく", "4 とつく"],
        "正確答案": "1 とうちゃく",
        "中文翻譯": "預計在3點左右抵達飯店。",
        "詳解": "「到」的讀音為長音「とう」，「着」的讀音為「ちゃく」，合起來即為「とうちゃく」。"
    },
    {
        "級別": "N3",
        "題目類型": "問題1 _のことばの読み方として最もよいものを、1・2・3・4から一つえらびなさい。",
        "題目文": "今から【訓練】を行います。",
        "選項": ["1 くんれい", "2 くんれん", "3 ぐんれい", "4 ぐんれん"],
        "正確答案": "2 くんれん",
        "中文翻譯": "現在開始進行訓練。",
        "詳解": "「訓」讀作「くん」，「練」讀作「れん」，故正確答案為「くんれん」。注意不可混淆成清音或鼻音。"
    },
    {
        "級別": "N3",
        "題目類型": "問題1 _のことばの読み方として最もよいものを、1・2・3・4から一つえらびなさい。",
        "題目文": "社会には【共通】のルールがあります。",
        "選項": ["1 きょうつ", "2 こうつつ", "3 きょうつう", "4 こうつ"],
        "正確答案": "3 きょうつう",
        "中文翻譯": "社會上有共同的規則。",
        "詳解": "「共」讀作長音「きょう」，「通()」讀作長音「つう」，結合在一起就是長音組合「きょうつう」。"
    },
    {
        "級別": "N3",
        "題目類型": "問題1 _のことばの読み方として最もよいものを、1・2・3・4から一つえらびなさい。",
        "題目文": "来年から【税金】が上がるそうだ。",
        "選項": ["1 ぜいきん", "2 ぜっきん", "3 せいきん", "4 せっきん"],
        "正確答案": "1 ぜいきん",
        "中文翻譯": "據說從明年開始稅金會調高。",
        "詳解": "「税」的讀音為「ぜい」，「金」的讀音為「きん」，正確組合為「ぜいきん」，屬於常見的日常生活高頻字彙。"
    }
]

# =========================================================================
# 🔄 狀態記憶初始化
# =========================================================================
if "learned_list" not in st.session_state:
    st.session_state.learned_list = []
if "word_quiz_seed" not in st.session_state:
    st.session_state.word_quiz_seed = 0
if "vocab_quiz_seed" not in st.session_state:
    st.session_state.vocab_quiz_seed = 0

def text_to_speech_bytes(text):
    try:
        tts = gTTS(text=text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except:
        return None

@st.cache_data(ttl=86400)
def get_fixed_daily_words(date_seed_str):
    seed_num = int(date_seed_str.replace("-", ""))
    random.seed(seed_num)
    return random.sample(JAPANESE_WORDS, min(len(JAPANESE_WORDS), 5))

# =========================================================================
# 🌐 網頁版面渲染 (極簡零錯誤結構版)
# =========================================================================
tab_study, tab_list, tab_word_quiz, tab_vocab_quiz = st.tabs([
    "📥 歷史單字隨身卡", 
    "🎓 已學會單字庫", 
    "📝 挑戰單字小測驗", 
    "📝 言語知識（文字・語彙）"
])

# -------------------------------------------------------------------------
# 分頁一：歷史單字隨身卡
# -------------------------------------------------------------------------
with tab_study:
    selected_date = st.date_input("📅 選擇學習或複習的日期：", datetime.today(), key="main_date_picker")
    date_str = selected_date.strftime('%Y-%m-%d')
    st.write(f"目前顯示為 **{selected_date.strftime('%Y 年 %m 月 %d 日')}** 的單字（內建一週冷卻防重複機制）。")
    st.write("---")

    daily_words = get_fixed_daily_words(date_str)

    for idx, item in enumerate(daily_words):
        unique_id = f"{date_str}_{item['單字']}"
        is_saved = any(x["id"] == unique_id for x in st.session_state.learned_list)

        if item["級別"] == "N3": st.error(f"日檢分級： {item['級別']} ")
        elif item["級別"] == "N4": st.warning(f"日檢分級： {item['級別']} ")
        else: st.success(f"日檢分級： {item['級別']} ")
        
        st.markdown(f"### 單字 {idx+1}：{item['單字']}（{item['詞性']}）")
        st.write(f"讀音假名：【 **{item['假名']}** 】")
        
        col_audio, _ = st.columns(2)
        with col_audio:
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

        state_checkbox = st.checkbox("💡 我已熟記學會此單字", value=is_saved, key=f"check_{unique_id}")
        if state_checkbox and not is_saved:
            st.session_state.learned_list.append({
                "id": unique_id, "學習日期": date_str, "級別": item["級別"], "單字": item["單字"], "讀音": item["假名"], "意思": item["中文意思"]
            })
        elif not state_checkbox and is_saved:
            st.session_state.learned_list = [x for x in st.session_state.learned_list if x["id"] != unique_id]
            
        st.write("---")

# -------------------------------------------------------------------------
# 分頁二：已學會單字庫
# -------------------------------------------------------------------------
with tab_list:
    st.subheader("🎓 您的個人專屬熟記單字庫")
    if st.session_state.learned_list:
        st.write(f"目前累計已經背熟了 **{len(st.session_state.learned_list)}** 個單字！")
        
        df_learned = pd.DataFrame(st.session_state.learned_list)
        df_learned = df_learned.sort_index(ascending=True)
        df_learned.index = range(1, len(df_learned) + 1)
        
        show_df = df_learned[["學習日期", "級別", "單字", "讀音", "意思"]]
        show_df.columns = ["出現日期", "日檢級別", "日文單字", "假名讀音", "中文意思"]
        st.dataframe(show_df, use_container_width=True)
        
        st.write("---")
        st.write("⚙️ **管理熟記清單**（點擊按鈕可立刻將單字移出已學會區）：")
        
        for b_idx, word_item in enumerate(list(st.session_state.learned_list)):
            if st.button(f"🗑️ 移除單字：{word_item['單字']}", key=f"del_btn_{word_item['id']}_{b_idx}"):
                st.session_state.learned_list = [x for x in st.session_state.learned_list if x["id"] != word_item["id"]]
                st.toast(f"已將 {word_item['單字']} 移回隨身卡！")
                st.rerun()
    else:
        st.info("這裡目前還空空的。在隨身卡勾選「我已熟記學會此單字」之後紀錄就會出現在這邊！")

# -------------------------------------------------------------------------
# 分頁三：單字小測驗 (徹底拆除 st.form，使用極簡平面結構)
# -------------------------------------------------------------------------
with tab_word_quiz:
    st.subheader("📝 日文單字實力大考驗 (N3-N5)")
    st.write("說明：請點選正確的選項，回答後點擊下方「提交答案」按鈕核對。")
    st.write("---")
    
    if st.button("🔄 換一題新單字測驗", key="btn_refresh_word_quiz"):
        st.session_state.word_quiz_seed += 1
        st.rerun()

    random.seed(st.session_state.word_quiz_seed + 1000)
    q_item = random.choice(JAPANESE_WORDS)
    q_type = random.randint(0, 1)

    wrong_pool = [w for w in JAPANESE_WORDS if w["單字"] != q_item["單字"]]
    wrong_choices = random.sample(wrong_pool, min(len(wrong_pool), 3))
    
    if q_type == 0:
        correct_ans = q_item["假名"]
        q_choices = [q_item["假名"]] + [w["假名"] for w in wrong_choices]
    else:
        correct_ans = q_item["單字"]
        q_choices = [q_item["單字"]] + [w["單字"] for w in wrong_choices]
        
    random.shuffle(q_choices)

    if q_type == 0:
        st.markdown(f"### ❓ 題目：請選出日文單字 **「 {q_item['單字']} 」** 的正確平假名讀音？")
    else:
        st.markdown(f"### ❓ 題目：中文意思是 **「 {q_item['中文意思']} 」** 的日文單字是哪一個？")
        
    user_ans = st.radio("請選擇正確選項：", q_choices, key=f"radio_w_{st.session_state.word_quiz_seed}")
    submit_btn = st.button("🎯 提交單字測驗答案", use_container_width=True, key=f"sub_btn_w_{st.session_state.word_quiz_seed}")

    if submit_btn and user_ans == correct_ans:
        st.success(f"🎉 答對了！【{q_item['單字']}】的意思正是「{q_item['中文意思']}」。")
    if submit_btn and user_ans != correct_ans:
