import streamlit as st
import pandas as pd
import random
from datetime import datetime
from gtts import gTTS
import io

# 1. 網頁基本設定
st.set_page_config(page_title="卡拉與小魚的日文言語知識大本營", layout="centered", page_icon="🇯🇵")

# =========================================================================
# 📚 核心日文單字庫
# =========================================================================
JAPANESE_WORDS = [
    {"級別": "N5", "單字": "學生", "假名": "がくせい", "詞性": "名詞", "中文意思": "學生", "例句": "私、學生です。", "例句假名": "わたしはがくせいです。", "例句中文": "我是學生。"},
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
# 📝 言語知識（文字・語彙）專屬模擬題庫 (不要閱讀短文)
# =========================================================================
VOCAB_QUIZZES = [
    {
        "級別": "N5",
        "題目類型": "漢字読解 (看漢字選讀音)",
        "題目文": "あそこに【留学生】がいます。",
        "選項": ["1. りゅうがくせい", "2. りゅがくせい", "3. りょうがくせい", "4. るがくせい"],
        "正確答案": "1. りゅうがくせい",
        "中文翻譯": "那裡有留學生。",
        "詳解": "【留学生】的正確平假名讀音為「りゅうがくせい」。注意「留」的長音為「りゅう」，「学」為「がく」，「生」為「せい」。"
    },
    {
        "級別": "N5",
        "題目類型": "表記 (看讀音選漢字)",
        "題目文": "まいにち、日本語を【べんきょう】します。",
        "選項": ["1. 勉強", "2. 強勉", "3. 勉強する", "4. 免強"],
        "正確答案": "1. 勉強",
        "中文翻譯": "每天都複習日文。",
        "詳解": "「べんきょう」對應的正確日文漢字為「勉強」。在日文中是指「學習、讀書」的意思。"
    },
    {
        "級別": "N4",
        "題目類型": "文脈規定 (語意選擇)",
        "題目文": "荷物が重いので、カバンを【　　】ください。",
        "選項": ["1. もって", "2. あけて", "3. しめて", "4. おいて"],
        "正確答案": "1. もって",
        "中文翻譯": "因為行李很重，請幫我拿包包。",
        "詳解": "根據上下文「荷物が重い（行李很重）」，最符合邏輯的動作是請人幫忙「拿（持って / もって）」。\n• あけて (打開)\n• しめて (關上)\n• おいて (放置)"
    },
    {
        "級別": "N3",
        "題目類型": "言い換え類義 (近義詞替換)",
        "題目文": "この問題は【だいたい】分かりました。",
        "選項": ["1. ほとんど", "2. ぜんぜん", "3. すこし", "4. かならず"],
        "正確答案": "1. ほとんど",
        "中文翻譯": "這個問題我大概都懂了。",
        "詳解": "「だいたい」意思是「大體上、大概、差不多」，與選項 1 的「ほとんど（大部分、幾乎）」意思最為接近。\n• ぜんぜん (完全不)\n• すこし (稍微)\n• かかならず (必定)"
    }
]

# =========================================================================
# 🔄 狀態記憶初始化
# =========================================================================
if "learned_list" not in st.session_state:
    st.session_state.learned_list = []
if "word_quiz_index" not in st.session_state:
    st.session_state.word_quiz_index = 0
if "vocab_quiz_index" not in st.session_state:
    st.session_state.vocab_quiz_index = 0

# 語音核心函數
def text_to_speech_bytes(text):
    try:
        tts = gTTS(text=text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except:
        return None

# 快取固定當天單字
@st.cache_data(ttl=86400)
def get_fixed_daily_words(date_seed_str):
    seed_num = int(date_seed_str.replace("-", ""))
    random.seed(seed_num)
    return random.sample(JAPANESE_WORDS, min(len(JAPANESE_WORDS), 5))

# =========================================================================
# 🌐 網頁版面渲染 (全新四功能大分頁)
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

        # 級別彩色標籤
        if item["級別"] == "N3": st.error(f"日檢分級： {item['級別']} ")
        elif item["級別"] == "N4": st.warning(f"日檢分級： {item['級別']} ")
        else: st.success(f"日檢分級： {item['級別']} ")
        
        # 單字挪到下方一行
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

        # 雙向同步打勾控制
        state_checkbox = st.checkbox("💡 我已熟記學會此單字", value=is_saved, key=f"check_{unique_id}")
        if state_checkbox and not is_saved:
            st.session_state.learned_list.append({
                "id": unique_id, "學習日期": date_str, "級別": item["級別"], "單字": item["單字"], "讀音": item["假名"], "意思": item["中文意思"]
            })
        elif not state_checkbox and is_saved:
            st.session_state.learned_list = [x for x in st.session_state.learned_list if x["id"] != unique_id]
            
        st.write("---")

# -------------------------------------------------------------------------
# 分頁二：已學會單字庫 (正序排列、1開始、支援無痛手動移除)
# -------------------------------------------------------------------------
with tab_list:
    st.subheader("🎓 您的個人專屬熟記單字庫")
    if st.session_state.learned_list:
        st.write(f"目前累計已經背熟了 **{len(st.session_state.learned_list)}** 個單字！")
        
        df_learned = pd.DataFrame(st.session_state.learned_list)
        df_learned = df_learned.sort_index(ascending=True) # 正序排列
        df_learned.index = range(1, len(df_learned) + 1) # 流水號從 1 開始
        
        show_df = df_learned[["學習日期", "級別", "單字", "讀音", "意思"]]
        show_df.columns = ["出現日期", "日檢級別", "日文單字", "假名讀音", "中文意思"]
        st.dataframe(show_df, use_container_width=True)
        
        st.write("---")
        st.write("⚙️ **管理熟記清單**（點擊按鈕可立刻將單字移出已學會區並解除單字卡打勾）：")
        
        for b_idx, word_item in enumerate(list(st.session_state.learned_list)):
            if st.button(f"🗑️ 移除單字：{word_item['單字']}", key=f"del_btn_item_id_{word_item['id']}_{b_idx}"):
                st.session_state.learned_list = [x for x in st.session_state.learned_list if x["id"] != word_item["id"]]
                st.toast(f"已將 {word_item['單字']} 移出已學會區。")
                st.rerun()
    else:
        st.info("這裡目前還空空的。在隨身卡勾選「我已熟記學會此單字」之後紀錄就會出現在這邊！")

# -------------------------------------------------------------------------
# 分頁三：單字小測驗 (全新安全穩定架構)
# -------------------------------------------------------------------------
with tab_word_quiz:
    st.subheader("📝 日文單字實力大考驗 (N3-N5)")
    st.write("說明：請點選正確的選項，回答後點擊下方「提交答案」按鈕核對。")
    st.write("---")
    
    # 點擊按鈕直接增加 index 做隨機，這能完全解決縮進與表單卡死問題
    if st.button("🔄 換一題新單字測驗", key="btn_refresh_word_quiz_main"):
        st.session_state.word_quiz_index += 1
        st.rerun()

    # 以計數器為種子碼固定題目，點擊提交絕對不閃退換題！
    random.seed(st.session_state.word_quiz_index + 100)
    q_item = random.choice(JAPANESE_WORDS)
    q_type = random.randint(0, 1) # 0為猜讀音，1為猜單字

    wrong_pool = [w for w in JAPANESE_WORDS if w["單字"] != q_item["單字"]]
    wrong_choices = random.sample(wrong_pool, min(len(wrong_pool), 3))
    
    if q_type == 0:
        correct_ans = q_item["假名"]
        q_choices = [q_item["假名"]] + [w["假名"] for w in wrong_choices]
    else:
        correct_ans = q_item["單字"]
        q_choices = [q_item["單字"]] + [w["單字"] for w in wrong_choices]
        
    random.shuffle(q_choices)

    with st.form(key=f"word_quiz_form_secured_{st.session_state.word_quiz_index}"):
        if q_type == 0:
            st.markdown(f"### ❓ 題目：請選出日文單字 **「 {q_item['單字']} 」** 的正確平假名讀音？")
        else:
            st.markdown(f"### ❓ 題目：中文意思是 **「 {q_item['中文意思']} 」** 的日文單字是哪一個？")
            
        user_ans = st.radio("請選擇正確選項：", q_choices, key=f"radio_choice_w_{st.session_state.word_quiz_index}")
        submit_btn = st.form_submit_button("🎯 提交答案", use_container_width=True)

    if submit_btn:
        if user_ans == correct_ans:
            st.success(f"🎉 答對了！【{q_item['單字']}】的意思正是「{q_item['中文意思']}」。")
        else:
            st.error(f"❌ 答錯囉！正確答案應該是：**{correct_ans}**。")

# -------------------------------------------------------------------------
# 分頁四：言語知識（文字・語彙） (全新安全穩定架構)
