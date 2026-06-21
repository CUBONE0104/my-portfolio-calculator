import streamlit as st

st.set_page_config(page_title="進階資產與曝險計算器", layout="centered")

st.title("📊 您的專屬資產曝險與報酬率計算器")
st.write("說明：本網頁所有金額欄位皆以 **萬元** 為單位。")
st.write("---")

# 側邊欄輸入：分為「成本」與「當前市值」
st.sidebar.header("🛠️ 1. 調整資產成本 (萬元)")
cost_00631l = st.sidebar.number_input("🚀 00631L 原始總成本", min_value=0.0, value=70.0, step=1.0)
cost_tsmc = st.sidebar.number_input("🇹🇼 台積電 原始總成本", min_value=0.0, value=25.0, step=1.0)
cost_others = st.sidebar.number_input("📈 其他個股 原始總成本", min_value=0.0, value=50.0, step=1.0)

st.sidebar.header("📈 2. 調整當前最新市值 (萬元)")
cash = st.sidebar.number_input("💵 現金持有金額", min_value=0.0, value=20.0, step=1.0)
mv_00631l = st.sidebar.number_input("🚀 00631L 當前總市值", min_value=0.0, value=90.0, step=1.0)
mv_tsmc = st.sidebar.number_input("🇹🇼 台積電 當前總市值", min_value=0.0, value=35.0, step=1.0)
mv_others = st.sidebar.number_input("📈 其他個股 當前總市值", min_value=0.0, value=55.0, step=1.0)

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

# 網頁上半部：資產規模與曝險
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
