import streamlit as st
import yfinance as yf

# 1. 網頁基本設定
st.set_page_config(page_title="雙十的個人投資空間", layout="centered", page_icon="💼")

# 2. 建立導覽列：將網頁轉型為「個人網站」
# 您可以自由在這裡增加更多分頁
page = st.sidebar.radio("🌐 導覽選單", ["關於我 & 首頁", "📊 資產與曝險計算器", "📈 投資理念"])

# -------------------------------------------------------------------------
# 分頁一：關於我 & 首頁
# -------------------------------------------------------------------------
if page == "關於我 & 首頁":
    st.title("👋 歡迎來到我的個人投資空間")
    st.write("這裡是我記錄投資想法、資產配置與開發投資工具的地方。")
    st.write("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # 可以換成您自己的頭像網址
        st.image("https://unsplash.com", width=150)
    with col2:
        st.subheader("關於我")
        st.write("• **投資風格**：指數化投資為主，搭配槓桿元件（正二）優化報酬。")
        st.write("• **研究領域**：資產配置、曝險控管、台美股市場。")
        st.write("• **聯絡信箱**：your_email@example.com")
        
    st.write("---")
    st.subheader("🛠️ 網站目前功能")
    st.info("請點選左側選單的 **「📊 資產與曝險計算器」** 來評估您當前的投資健康度。")

# -------------------------------------------------------------------------
# 分頁二：資產與曝險計算器 (核心功能修改)
# -------------------------------------------------------------------------
elif page == "📊 資產與曝險計算器":
    st.title("📊 您的專屬資產曝險與報酬率計算器")
    st.write("說明：本網頁所有金額欄位皆以 **萬元** 為單位。")
    st.write("---")

    # 獲取最新即時股價 (台股代號需加上 .TW)
    @st.cache_data(ttl=3600)  # 快取一小時，避免重複請求變慢
    def get_stock_prices():
        try:
            p_00631l = yf.Ticker("00631L.TW").fast_info['last_price']
            p_tsmc = yf.Ticker("2330.TW").fast_info['last_price']
            return p_00631l, p_tsmc
        except:
            return 230.0, 1000.0  # 若 API 故障時的預設保底股價

    price_00631l, price_tsmc = get_stock_prices()

    # 側邊欄輸入：調整為輸入「原始成本」與「持有股數」
    st.sidebar.header("🛠️ 1. 調整資產成本 (萬元)")
    cost_00631l = st.sidebar.number_input("🚀 00631L 原始總成本", min_value=0.0, value=70.0, step=1.0)
    cost_tsmc = st.sidebar.number_input("🇹🇼 台積電 原始總成本", min_value=0.0, value=25.0, step=1.0)
    cost_others = st.sidebar.number_input("📈 其他個股 原始總成本", min_value=0.0, value=50.0, step=1.0)

    st.sidebar.header("📈 2. 輸入持有股數 (自動算市值)")
    
    # 顯示目前抓到的股價供用戶參考
    st.sidebar.caption(f"當前即時參考股價：00631L: {price_00631l} 元 | 台積電: {price_tsmc} 元")
    
    shares_00631l = st.sidebar.number_input("🚀 00631L 持有股數 (股)", min_value=0, value=4000, step=100)
    shares_tsmc = st.sidebar.number_input("🇹🇼 台積電 持有股數 (股)", min_value=0, value=350, step=10)
    
    # 其他個股與現金因為變數較多，保留手動輸入萬元
    mv_others = st.sidebar.number_input("📈 其他個股 當前總市值 (萬元)", min_value=0.0, value=55.0, step=1.0)
    cash = st.sidebar.number_input("💵 現金持有金額 (萬元)", min_value=0.0, value=20.0, step=1.0)

    # 自動計算當前市值 (股數 * 股價 / 10000 = 萬元)
    mv_00631l = (shares_00631l * price_00631l) / 10000
    mv_tsmc = (shares_tsmc * price_tsmc) / 10000

    # 核心數學計算
    total_cost = cost_00631l + cost_tsmc + cost_others
    total_market_value = cash + mv_00631l + mv_tsmc + mv_others
    total_stock_mv = mv_00631l + mv_tsmc + mv_others

    # 報酬率計算
    roi_00631l = ((mv_00631l - cost_00631l) / cost_00631l * 100) if cost_00631l > 0 else 0.0
    roi_tsmc = ((mv_tsmc - cost_tsmc) / cost_tsmc * 100) if cost_tsmc > 0 else 0.0
    roi_others = ((mv_others - cost_others) / cost_others * 100) if cost_others > 0 else 0.0
    total_stock_profit = total_stock_mv - total_cost
    total_roi = (total_stock_profit / total_cost * 100) if total_cost > 0 else 0.0

    # 實質市場曝險總市值 (正2乘以2倍)
    exposure_market_value = (mv_00631l * 2) + mv_tsmc + mv_others
    exposure_ratio = (exposure_market_value / total_market_value) if total_market_value > 0 else 0.0

    # 顯示自動計算出的市值結果
    st.subheader("💡 自動市值換算結果")
    cx1, cx2 = st.columns(2)
    cx1.write(f"🚀 **00631L 目前估值**: {mv_00631l:.2f} 萬元")
    cx2.write(f"🇹🇼 **台積電 目前估值**: {mv_tsmc:.2f} 萬元")

    # 網頁上半部：資產規模與曝險
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 當前總資產規模", f"{total_market_value:.1f} 萬元")
    with col2:
        st.metric("🎯 實質曝險比率", f"{exposure_ratio:.3f} ({exposure_ratio*100:.1f}%)")

    # 網頁中部：曝險健康度
    st.write("---")
    st.subheader("🔍 曝險健康度評估")
    if 1.35 <= exposure_ratio <= 1.50:
        st.success(f"✅ 狀態安全：當前曝險為 **{exposure_ratio:.2f}**，符合 1.35 - 1.50 黃金區間。")
    elif exposure_ratio > 1.50:
        st.error(f"⚠️ 警訊：曝險過高！已超出上限 1.50。")
        suggested_reduce = exposure_market_value - (1.5 * total_market_value)
        st.info(f"💡 建議：可將約 **{suggested_reduce/2:.1f} 萬元** 的 00631L 獲利了結轉為現金。")
    else:
        st.warning(f"ℹ️ 提示：目前曝險低於 1.35。")

    # 網頁下半部：報酬率看板
    st.write("---")
    st.subheader("📈 投資報酬率看板")

    # 總績效
    st.metric("🏆 股票總帳面損益", f"+{total_stock_profit:.1f} 萬元", f"總投報率 +{total_roi:.2f}%")

    # 各檔細節
    c1, c2, c3 = st.columns(3)
    c1.metric("🚀 00631L 績效", f"{mv_00631l:.1f} 萬", f"報酬率 {roi_00631l:+.1f}%")
    c2.metric("🇹🇼 台積電 績效", f"{mv_tsmc:.1f} 萬", f"報酬率 {roi_tsmc:+.1f}%")
    c3.metric("📈 其他個股", f"{mv_others:.1f} 萬", f"報酬率 {roi_others:+.1f}%")

# -------------------------------------------------------------------------
# 分頁三：投資理念
# -------------------------------------------------------------------------
elif page == "📈 投資理念":
    st.title("投資備忘錄")
    st.write("這裡記錄我的核心投資心法，用來提醒自己在市場波動時保持理性。")
    st.write("---")
    st.markdown("""
    ### 🧠 我的核心策略
    1. **槓桿控管**：利用元大台灣50正2 (00631L) 放大經費效率，但實質市場曝險嚴格控制在 **1.35 - 1.50** 之間。
    2. **長期持有**：相信台灣半導體與台積電的長期競爭力。
    3. **定期動態平衡**：當曝險超出上限時，強迫自己獲利了結，留存現金。
    """)
