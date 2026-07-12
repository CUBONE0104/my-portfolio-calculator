import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from gtts import gTTS
import io

# 1. 網頁基本設定
st.set_page_config(page_title="卡拉與小魚的日文單字隨身卡", layout="centered", page_icon="🇯🇵")

# =========================================================================
# 📚 核心日文單字庫 (精選 11 個單字，未來可自行無限擴充)
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
# 🔄 狀態初始化
# =========================================================================
if "learned_list" not in st.session_state:
    st.session_state.learned_list = []

# 用於紀錄過去 7 天內每天各自出現過什麼單字，來做到「一週內不重複」
if "history_7_days" not in st.session_state:
    st.session_state.history_7_days = {}

def text_to_speech_bytes(text):
    try:
        tts = gTTS(text=text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except:
        return None

# 需求 3：冷卻演算核心 — 自動過濾掉過去七天看過的單字
def get_smart_daily_words(target_date):
    date_str = target_date.strftime('%Y-%m-%d')
    
    # 1. 撈出過去 7 天內所有生成過的單字名單
    recently_seen = set()
    for i in range(1, 8):
        prev_date = (target_date - timedelta(days=i)).strftime('%Y-%m-%d')
        if prev_date in st.session_state.history_7_days:
            recently_seen.update(st.session_state.history_7_days[prev_date])
            
    # 2. 過濾掉七天內出現過的字
    pool = [w for w in JAPANESE_WORDS if w["單字"] not in recently_seen]
    
    # 防禦機制：若庫存太少不夠扣，就直接用全字庫抽
    if len(pool) < 5:
        pool = JAPANESE_WORDS
        
    # 3. 以當天日期為隨機種子抽 5 個字
    seed_num = int(target_date.strftime('%Y%m%d'))
    random.seed(seed_num)
    chosen_words = random.sample(pool, min(len(pool), 5))
    
    # 4. 登記到歷史紀錄中
    st.session_state.history_7_days[date_str] = [w["單字"] for w in chosen_words]
    return chosen_words

# 測驗抽題核心回呼
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

# =========================================================================
# 🌐 網頁版面渲染
# =========================================================================
st.title("🇯🇵 N3-N5 智慧日文學習大本營")
tab_study, tab_list, tab_quiz = st.tabs(["📥 歷史單字隨身卡", "🎓 已學會單字庫", "📝 挑戰日文小測驗"])

with tab_study:
    selected_date = st.date_input("📅 選擇學習或複習的日期：", datetime.today())
    date_str = selected_date.strftime('%Y-%m-%d')
    st.write(f"目前顯示為 **{selected_date.strftime('%Y 年 %m 月 %d 日')}** 的單字（內建一週冷卻防重複機制）。")
    st.write("---")

    daily_words = get_smart_daily_words(selected_date)

    for idx, item in enumerate(daily_words):
        unique_id = f"{date_str}_{item['單字']}"
        is_saved = any(x["id"] == unique_id for x in st.session_state.learned_list)

        # 需求 1：彩色標籤獨立在第一行
        if item["級別"] == "N3": st.error(f"日檢分級： {item['級別']} ")
        elif item["級別"] == "N4": st.warning(f"日檢分級： {item['級別']} ")
        else: st.success(f"日檢分級： {item['級別']} ")
        
        # 單字獨立在第二行
        st.markdown(f"### 單字 {idx+1}：{item['單字']}（{item['詞性']}）")
        st.write(f"讀音假名：【 **{item['假名']}** 】")
        
        # 需求 2：迷你版語音條
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

        # 打勾加入功能
        state_checkbox = st.checkbox("💡 我已熟記學會此單字", value=is_saved, key=f"check_{unique_id}")
        if state_checkbox and not is_saved:
            st.session_state.learned_list.append({
                "id": unique_id, "學習日期": date_str, "級別": item["級別"], "單字": item["單字"], "讀音": item["假名"], "意思": item["中文意思"]
            })
        elif not state_checkbox and is_saved:
            st.session_state.learned_list = [x for x in st.session_state.learned_list if x["id"] != unique_id]
            
        st.write("---")

# 需求 1 & 2：已學會清單正序排列（從 1 開始）＋ 支援手動移除按鈕
with tab_list:
    st.subheader("🎓 您的個人專屬熟記單字庫")
    if st.session_state.learned_list:
        st.write(f"目前累計已經背熟了 **{len(st.session_state.learned_list)}** 個單字！")
        
        df_learned = pd.DataFrame(st.session_state.learned_list)
        df_learned = df_learned.sort_index(ascending=True) # 時間正序排列
        df_learned.index = range(1, len(df_learned) + 1) # 流水號從 1 開始
        
        show_df = df_learned[["學習日期", "級別", "單字", "讀音", "意思"]]
        show_df.columns = ["出現日期", "日檢級別", "日文單字", "假名讀音", "中文意思"]
        st.dataframe(show_df, use_container_width=True)
        
        # 需求 1：手動單字移除鈕（代表突然又不會了）
        st.write("---")
        st.write("⚙️ **管理熟記清單**（點擊下方按鈕可立刻移出已學會區）：")
        for word_item in list(st.session_state.learned_list):
            if st.button(f"🗑️ 移除單字：{word_item['單字']}", key=f"del_btn_{word_item['id']}"):
                st.session_state.learned_list = [x for x in st.session_state.learned_list if x["id"] != word_item["id"]]
                st.toast(f"已將 {word_item['單字']} 移出已學會區。")
                st.rerun()
    else:
        st.info("這裡目前還空空的。在隨身卡勾選「學會了」之後紀錄就會出現在這邊！")

# 需求 3：全面修復、絕不閃退的日文測驗區
with tab_quiz:
    st.subheader("📝 日文實力大考驗 (N3-N5)")
    st.write("說明：請點選正確的選項，回答後點擊下方「提交答案」按鈕核對。")
    st.write("---")
    
    if "quiz_item" not in st.session_state:
        generate_new_quiz()

    st.button("🔄 換一題新測驗", on_click=generate_new_quiz, key="refresh_quiz_btn")

    q_item = st.session_state.quiz_item
    q_type = st.session_state.quiz_type
    q_choices = st.session_state.quiz_choices

    with st.form(key="pure_japanese_quiz_form"):
        if q_type == 0:
            st.markdown(f"### ❓ 題目：請選出日文單字 **「 {q_item['單字']} 」** 的正確平假名讀音？")
            correct_ans = q_item["假名"]
        else:
            st.markdown(f"### ❓ 題目：中文意思是 **「 {q_item['中文意思']} 」** 的日文單字是哪一個？")
            correct_ans = q_item["單字"]
            
        user_ans = st.radio("請選擇正確選項：", q_choices, key="quiz_form_radio")
        submit_btn = st.form_submit_button("🎯 提交答案", use_container_width=True)

    if submit_btn:
        if user_ans == correct_ans:
            st.success(f"🎉 完全答對！【{q_item['單字']}】的意思正是「{q_item['中文意思']}」。")
            st.balloons()
        else:
            st.error(f"❌ 再接再厲！正確答案應該是：**{correct_ans}**。")
