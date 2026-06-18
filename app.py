import os
import sys

# 🚀 終極防錯：自動檢查並安裝缺失的套件
required_packages = ["yfinance", "pandas", "plotly"]
for pkg in required_packages:
    try:
        __import__(pkg)
    except ModuleNotFoundError:
        os.system(f"{sys.executable} -m pip install {pkg}")

import streamlit as st
import yfinance as yf
import pandas as pd

# ==========================================
# 1. 介面基礎設定
# ==========================================
st.set_page_config(
    page_title="八大金剛 - 長倉必勝火控雷達", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🪣 500萬水庫火控雷達")
st.markdown("**長倉必勝！舊倉看賣，新金買息。(智能「股息 + PE」雙重火控版)**")
st.divider()

# ==========================================
# 2. 核心數據庫 (純手動精準派息 + 嚴格 PE 防線)
# ==========================================
stocks_config = {
    "0941.HK": {"name": "中移動", "min_yield": 5.8, "golden_yield": 6.7, "max_pe": 12.0, "tax_rate": 0.10, "shares": 500, "dps": 4.83},
    "0883.HK": {"name": "中海油", "min_yield": 6.3, "golden_yield": 7.6, "max_pe": 10.0, "tax_rate": 0.10, "shares": 5000, "dps": 1.45},
    "0002.HK": {"name": "中電", "min_yield": 4.5, "golden_yield": 5.5, "max_pe": 20.0, "tax_rate": 0.00, "shares": 1000, "dps": 3.10},
    "3988.HK": {"name": "中銀", "min_yield": 6.7, "golden_yield": 7.6, "max_pe": 6.0, "tax_rate": 0.10, "shares": 0, "dps": 0.26},
    "1038.HK": {"name": "長建", "min_yield": 5.0, "golden_yield": 6.0, "max_pe": 16.0, "tax_rate": 0.00, "shares": 0, "dps": 2.50},
    "0005.HK": {"name": "滙控", "min_yield": 6.5, "golden_yield": 7.5, "max_pe": 10.0, "tax_rate": 0.00, "shares": 0, "dps": 4.80},
    "1883.HK": {"name": "CTM", "min_yield": 7.5, "golden_yield": 8.5, "max_pe": 15.0, "tax_rate": 0.00, "shares": 0, "dps": 0.19},
    "1088.HK": {"name": "中國神華", "min_yield": 6.7, "golden_yield": 8.1, "max_pe": 10.0, "tax_rate": 0.10, "shares": 0, "dps": 2.2389}
}

# ==========================================
# 3. 動態數據抓取 (同時抓取 股價 與 實時 PE)
# ==========================================
@st.cache_data(ttl=300)
def fetch_stock_market_data(ticker_code):
    try:
        ticker = yf.Ticker(ticker_code)
        hist = ticker.history(period="1d")
        
        # 抓股價
        if not hist.empty:
            price = round(hist['Close'].iloc[-1], 3)
        else:
            price = round(ticker.fast_info.get('lastPrice', 0), 3)
            
        # 抓網上實時市盈率 (TTM PE)
        info = ticker.info
        pe = info.get('trailingPE', None)
        
        return {"price": price, "pe": pe}
    except Exception:
        return None

# 預先加載所有市場數據
market_data_cache = {}
for ticker_code in stocks_config.keys():
    market_data_cache[ticker_code] = fetch_stock_market_data(ticker_code)

# ==========================================
# 4. 💼 實時持倉與水庫狀態面版
# ==========================================
st.subheader("💼 實時持倉與水庫狀態")

total_market_value = 0
total_annual_dividend = 0
portfolio_data = []

for ticker_code, config in stocks_config.items():
    m_data = market_data_cache[ticker_code]
    if m_data is None or m_data["price"] == 0: continue
    
    current_price = m_data["price"]
    shares = config["shares"]
    net_dps = config["dps"] * (1 - config["tax_rate"])
    
    if shares > 0:
        market_value = current_price * shares
        expected_div = net_dps * shares
        
        total_market_value += market_value
        total_annual_dividend += expected_div
        
        portfolio_data.append({
            "股票": config["name"],
            "股數": f"{shares:,}",
            "現價 ($)": f"{current_price:.2f}",
            "持倉市值 ($)": market_value,
            "預計全年收息 ($)": expected_div
        })

col1, col2 = st.columns(2)
col1.metric(label="💰 總持倉市值", value=f"${total_market_value:,.2f}")
col2.metric(label="🚰 預計全年淨被動收入", value=f"${total_annual_dividend:,.2f}")

if portfolio_data:
    df_portfolio = pd.DataFrame(portfolio_data)
    st.dataframe(
        df_portfolio.style.format({"持倉市值 ($)": "{:,.2f}", "預計全年收息 ($)": "{:,.2f}"}),
        hide_index=True, 
        use_container_width=True
    )
else:
    st.info("目前尚未建立任何持倉（請在代碼中的 stocks_config 修改 shares 數量）。")

st.divider()

# ==========================================
# 5. 📊 實時火控監測面版 (引入 PE 判定安全鎖)
# ==========================================
st.subheader("📊 實時火控監測面版")

for ticker_code, config in stocks_config.items():
    m_data = market_data_cache[ticker_code]
    
    if m_data is None or m_data["price"] == 0:
        st.error(f"❌ 網絡超時：無法獲取 {config['name']} ({ticker_code}) 數據。")
        continue
        
    current_price = m_data["price"]
    current_pe = m_data["pe"]
    
    # 計算實質息率
    net_dps = config["dps"] * (1 - config["tax_rate"])
    current_yield = (net_dps / current_price) * 100
    max_fire_price = net_dps / (config["min_yield"] / 100)
    
    # 🌟 【核心修訂】雙重條件判定：股息率要夠高，而且實時 PE 必須小於或等於 max_pe 防守線
    yield_pass = current_yield >= config["min_yield"]
    pe_pass = (current_pe is None) or (current_pe <= config["max_pe"]) # 如果網上漏數據則以股息為主放行
    
    if yield_pass and pe_pass:
        status_icon = "🟢"
        is_green = True
    else:
        status_icon = "🔻"
        is_green = False
        premium = ((config["min_yield"] / current_yield) - 1) * 100

    pe_display = f"{current_pe:.1f} 倍" if current_pe is not None else "暫無數據"
    expander_title = f"{status_icon} {config['name']} ({ticker_code}) - 現價: ${current_price:.2f} | 實質息率: {current_yield:.2f}% | 實時 PE: {pe_display}"
    
    with st.expander(expander_title, expanded=True):
        st.write(f"**防禦防線：** 淺綠息率 {config['min_yield']:.1f}% (上限 PE: {config['max_pe']:.1f}倍) | 深綠黃金線 {config['golden_yield']:.1f}%")
        st.caption(f"✍️ *手動固定派息設定：${config['dps']:.4f} (未扣稅)*")
        
        if is_green:
            st.success(
                f"🍏 **雙重大綠燈！** 目前實質息率 {current_yield:.2f}% 已達標，且實時市盈率 ({pe_display}) 位處安全線內。\n\n"
                f"**戰術：** 估值合理且回報足夠，啟動常規步兵分批建倉（最高合理買入價 ${max_fire_price:.2f}）。"
            )
        else:
            # 區分開火失敗的原因
            if yield_pass and not pe_pass:
                st.error(
                    f"⚠️ **高息估值過高警告！** 雖然目前落袋息率有 {current_yield:.2f}% 達標，但實時 PE ({pe_display}) 已經高過安全上限 {config['max_pe']:.1f} 倍！\n\n"
                    f"**戰術：** 觸發安全制動！代表市場可能預期盈利將大幅倒退，拒絕開火，繼續鎖死保險箱觀察！"
                )
            else:
                st.warning(
                    f"🔴 **紅燈警戒！** 股息率未達伏擊圈，距離淺綠開火線尚有 **+{premium:.1f}%** 溢價（目標開火價 ${max_fire_price:.2f}）。\n\n"
                    f"**戰術：** 忍手！將子彈留給未來的特價區。"
                )
