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
import datetime

# ==========================================
# 1. 介面基礎設定
# ==========================================
st.set_page_config(
    page_title="八大金剛 - 長倉必勝火控雷達", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🪣 500萬水庫火控雷達")
st.markdown("**長倉必勝！舊倉看買，新金買息。 (全面自動化歷史股息版)**")
st.divider()

# ==========================================
# 2. 核心數據庫 (已徹底拔除 expected_dps 預計派息欄位)
# ==========================================
stocks_config = {
    "0941.HK": {"name": "中移動", "min_yield": 6.5, "golden_yield": 7.5, "max_pe": 12, "tax_rate": 0.10, "shares": 500},
    "0883.HK": {"name": "中海油", "min_yield": 6.0, "golden_yield": 8.0, "max_pe": 10, "tax_rate": 0.10, "shares": 5000},
    "0002.HK": {"name": "中電", "min_yield": 4.2, "golden_yield": 5.0, "max_pe": 20, "tax_rate": 0.00, "shares": 1000},
    "3988.HK": {"name": "中銀", "min_yield": 7.0, "golden_yield": 8.5, "max_pe": 6, "tax_rate": 0.10, "shares": 0},
    "1038.HK": {"name": "長建", "min_yield": 4.8, "golden_yield": 5.8, "max_pe": 16, "tax_rate": 0.00, "shares": 0},
    "0005.HK": {"name": "滙控", "min_yield": 6.5, "golden_yield": 8.0, "max_pe": 10, "tax_rate": 0.00, "shares": 0},
    "1883.HK": {"name": "CTM", "min_yield": 8.0, "golden_yield": 9.5, "max_pe": 15, "tax_rate": 0.00, "shares": 0},
    "1088.HK": {"name": "中國神華", "min_yield": 7.0, "golden_yield": 8.5, "max_pe": 10, "tax_rate": 0.10, "shares": 0}
}

# ==========================================
# 3. 100% 純自動歷史數據抓取邏輯 (快取 5 分鐘)
# ==========================================
@st.cache_data(ttl=300)
def fetch_stock_data(ticker_code, config):
    try:
        ticker = yf.Ticker(ticker_code)
        
        # 1. 抓取實時現價
        hist = ticker.history(period="1d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
        else:
            current_price = ticker.fast_info.get('lastPrice', None)
            
        if current_price is None or current_price == 0:
            return None
            
        # 2. 100% 自動抓取上一個年度 (2025年) 的真實總派息
        last_year = datetime.datetime.now().year - 1
        divs = ticker.dividends
        
        last_year_dps = 0
        if not divs.empty:
            last_year_dps = divs[divs.index.year == last_year].sum()
            
        # 防護機制：如果 yfinance 歷史數據庫未更新完畢導致算出來是 0，直接對接官方實時歷史實際派息金額 (TTM Rate)
        if last_year_dps == 0 or pd.isna(last_year_dps):
            last_year_dps = ticker.info.get('trailingAnnualDividendRate', 0)
            if last_year_dps is None:
                last_year_dps = 0
                
        return {
            "current_price": round(current_price, 3),
            "annual_dps": float(last_year_dps)
        }
    except Exception:
        return None

# 預先加載所有數據
stock_data_cache = {}
for ticker_code, config in stocks_config.items():
    stock_data_cache[ticker_code] = fetch_stock_data(ticker_code, config)

# ==========================================
# 4. 💼 實時持倉與水庫狀態面版
# ==========================================
st.subheader("💼 實時持倉與水庫狀態")

total_market_value = 0
total_annual_dividend = 0
portfolio_data = []

for ticker_code, config in stocks_config.items():
    data = stock_data_cache[ticker_code]
    if data is None: continue
    
    shares = config["shares"]
    current_price = data["current_price"]
    # 自動計算上年實際派息扣稅後的淨股息
    net_dps = data["annual_dps"] * (1 - config["tax_rate"])
    
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

# 顯示水庫總計
col1, col2 = st.columns(2)
col1.metric(label="💰 總持倉市值", value=f"${total_market_value:,.2f}")
col2.metric(label="🚰 上年實際股息計算 - 預計全年淨被動收入", value=f"${total_annual_dividend:,.2f}")

# 顯示持倉表格
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
# 5. 📊 實時火控監測面版
# ==========================================
st.subheader("📊 實時火控監測面版")

for ticker_code, config in stocks_config.items():
    data = stock_data_cache[ticker_code]
    
    if data is None:
        st.error(f"❌ 網絡超時：無法獲取 {config['name']} ({ticker_code}) 數據。")
        continue
        
    current_price = data["current_price"]
    net_dps = data["annual_dps"] * (1 - config["tax_rate"])
    current_yield = (net_dps / current_price) * 100
    max_fire_price = net_dps / (config["min_yield"] / 100)
    
    if current_yield >= config["min_yield"]:
        status_icon = "🟢"
        is_green = True
    else:
        status_icon = "🔻"
        is_green = False
        premium = ((config["min_yield"] / current_yield) - 1) * 100

    expander_title = f"{status_icon} {config['name']} ({ticker_code}) - 現價: ${current_price:.2f} | 實質歷史息率: {current_yield:.2f}%"
    
    with st.expander(expander_title, expanded=True):
        st.write(f"**防禦設定：** 淺綠線 {config['min_yield']:.1f}% | 深綠黃金線 {config['golden_yield']:.1f}%")
        st.write(f"ℹ️ *系統已全自動抓取上年實際每股派息計數：${data['annual_dps']:.3f} (未扣稅)*")
        
        if is_green:
            st.success(
                f"🍏 **淺綠燈！** 目前實質歷史息率 {current_yield:.2f}% 已進入常規伏擊圈（最高開火價 ${max_fire_price:.2f}）。\n\n"
                f"**戰術：** 配合每月出糧資金，啟動常規步兵分批建倉。"
            )
        else:
            st.warning(
                f"🔴 **紅燈！** 距離淺綠開火線尚有 **+{premium:.1f}%** 溢價（目標開火價 ${max_fire_price:.2f}）。\n\n"
                f"**戰術：** 忍手！保險箱鎖死，將子彈留給未來的特價區。"
            )
