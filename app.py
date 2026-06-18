import os
import sys

# 🚀 終極防錯：自動檢查並安裝缺失的套件（解決 Streamlit 雲端環境有時無視 requirements.txt 的問題）
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

# 1. 介面基礎設定（完美適應 iPhone/iPad 螢幕）
st.set_page_config(
    page_title="八大金剛 - 長倉必勝火控雷達", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🪣 500萬水庫火控雷達")
st.markdown("**長倉必勝！舊倉看買，新金買息。**")

# 2. 核心數據庫 - 八大金剛防禦線與參數設定
# (expected_dps 已預設更新為最新數值，並作為 yfinance 網絡出錯時的防護安全備用數)
stocks_config = {
    "0941.HK": {"name": "中移動", "min_yield": 6.5, "golden_yield": 7.5, "max_pe": 12, "expected_dps": 4.83, "tax_rate": 0.10, "shares": 500},
    "0883.HK": {"name": "中海油", "min_yield": 6.0, "golden_yield": 8.0, "max_pe": 10, "expected_dps": 1.45, "tax_rate": 0.10, "shares": 5000},
    "0002.HK": {"name": "中電", "min_yield": 4.2, "golden_yield": 5.0, "max_pe": 20, "expected_dps": 3.10, "tax_rate": 0.00, "shares": 1000},
    "3988.HK": {"name": "中銀", "min_yield": 7.0, "golden_yield": 8.5, "max_pe": 6, "expected_dps": 0.26, "tax_rate": 0.10, "shares": 0},
    "1038.HK": {"name": "長建", "min_yield": 4.8, "golden_yield": 5.8, "max_pe": 16, "expected_dps": 2.50, "tax_rate": 0.00, "shares": 0},
    "0005.HK": {"name": "滙控", "min_yield": 6.5, "golden_yield": 8.0, "max_pe": 10, "expected_dps": 4.80, "tax_rate": 0.00, "shares": 1000},
    "1883.HK": {"name": "CTM", "min_yield": 8.0, "golden_yield": 9.5, "max_pe": 15, "expected_dps": 0.19, "tax_rate": 0.00, "shares": 2000}
}

# 3. 動態數據抓取邏輯（加入 5 分鐘快取，避免頻繁刷網頁導致被 Yahoo 封鎖 IP）
@st.cache_data(ttl=300)
def fetch_stock_data(ticker_code, config):
    try:
        ticker = yf.Ticker(ticker_code)
        
        # 獲取實時現價
        hist = ticker.history(period="1d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
        else:
            current_price = ticker.fast_info.get('lastPrice', None)
            
        if current_price is None or current_price == 0:
            return None
            
        # ⚙️ 自動獲取上一個年度（2025年）的所有歷史派息紀錄
        last_year = datetime.datetime.now().year - 1
        divs = ticker.dividends
        
        if not divs.empty:
            # 篩選並加總 2025 年的總派息
            last_year_dps = divs[divs.index.year == last_year].sum()
        else:
            last_year_dps = 0
            
        # 如果 yfinance 抓取歷史數據回傳 0，就動態落入防護機制：採用 config 內的儲備數字
        if last_year_dps == 0:
            last_year_dps = config["expected_dps"]
            
        return {
            "current_price": round(current_price, 2),
            "annual_dps": last_year_dps
        }
    except Exception:
        # 出現網絡或解析錯誤時的安全回退機制
        return None

# 4. 渲染前端火控面板
st.subheader("📊 實時火控監測面版")

for ticker_code, config in stocks_config.items():
    data = fetch_stock_data(ticker_code, config)
    
    if data is None:
        st.error(f"❌ 網絡超時：無法獲取 {config['name']} ({ticker_code}) 數據。")
        continue
        
    current_price = data["current_price"]
    annual_dps = data["annual_dps"]
    
    # 計算扣除股息稅後的「真正落袋股息率」
    net_dps = annual_dps * (1 - config["tax_rate"])
    current_yield = (net_dps / current_price) * 100
    
    # 計算最高開火價 (當達到目標 min_yield 時的合理股價)
    max_fire_price = net_dps / (config["min_yield"] / 100)
    
    # 判斷號訊燈狀態與溢價計算
    if current_yield >= config["min_yield"]:
        status_icon = "🟢"
        is_green = True
    else:
        status_icon = "🔻"
        is_green = False
        # 計算現價高出開火價的「溢價百分比」
        premium = ((config["min_yield"] / current_yield) - 1) * 100

    # 建立摺疊選單 (Expander)
    expander_title = f"{status_icon} {config['name']} ({ticker_code}) - 現價: ${current_price:.2f} | 實質息率: {current_yield:.2f}%"
    
    with st.expander(expander_title, expanded=True):
        st.write(f"**防禦設定：** 淺綠線 {config['min_yield']:.1f}% | 深綠黃金線 {config['golden_yield']:.1f}%")
        
        if is_green:
            st.success(
                f"🍏 **淺綠燈！** 目前實質息率 {current_yield:.2f}% 已進入常規伏擊圈（最高開火價 ${max_fire_price:.2f}）。\n\n"
                f"**戰術：** 配合每月出糧資金，啟動常規步兵分批建倉。"
            )
        else:
            st.warning(
                f"🔴 **紅燈！** 距離淺綠開火線尚有 **+{premium:.1f}%** 溢價（目標開火價 ${max_fire_price:.2f}）。\n\n"
                f"**戰術：** 忍手！保險箱鎖死，將子彈留給未來的特價區。"
            )
