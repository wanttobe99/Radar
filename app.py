import os
import sys
import time
import random
import requests

# 🚀 終極防錯：自動檢查並安裝缺失的套件
required_packages = ["yfinance", "pandas", "plotly", "requests"]
for pkg in required_packages:
    try:
        __import__(pkg)
    except ModuleNotFoundError:
        os.system(f"{sys.executable} -m pip install {pkg}")

import streamlit as st
import yfinance as yf
import pandas as pd

# 建立帶有偽裝的 Session，解決 Streamlit IP 容易被 Block 的問題
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# ==========================================
# 1. 介面基礎設定
# ==========================================
st.set_page_config(
    page_title="八大金剛 - 長倉必勝火控雷達", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🎯 500萬水庫火控雷達 (100% 港股純防禦陣型)")
st.markdown("**長倉必勝！舊倉看賣，新金買息。(智能「股息 + PE + 派息比率」三重火控版)**")
st.divider()

# ==========================================
# 2. 核心數據庫 (保留手動 DPS 作為終極後備)
# ==========================================
stocks_config = {
    "0941.HK": {"name": "中移動", "min_yield": 5.8, "golden_yield": 6.7, "max_pe": 12.0, "tax_rate": 0.10, "shares": 500, "manual_dps": 5.27},
    "0883.HK": {"name": "中海油", "min_yield": 6.3, "golden_yield": 7.6, "max_pe": 10.0, "tax_rate": 0.10, "shares": 5000, "manual_dps": 1.28},
    "0002.HK": {"name": "中電", "min_yield": 4.5, "golden_yield": 5.5, "max_pe": 20.0, "tax_rate": 0.00, "shares": 1000, "manual_dps": 3.20},
    "3988.HK": {"name": "中銀", "min_yield": 6.7, "golden_yield": 7.6, "max_pe": 6.0, "tax_rate": 0.10, "shares": 0, "manual_dps": 0.2531},
    "1038.HK": {"name": "長建", "min_yield": 5.0, "golden_yield": 6.0, "max_pe": 16.0, "tax_rate": 0.00, "shares": 0, "manual_dps": 2.61},
    "0005.HK": {"name": "滙控", "min_yield": 6.5, "golden_yield": 7.5, "max_pe": 10.0, "tax_rate": 0.00, "shares": 0, "manual_dps": 5.857},
    "1883.HK": {"name": "CTM", "min_yield": 7.5, "golden_yield": 8.5, "max_pe": 15.0, "tax_rate": 0.00, "shares": 0, "manual_dps": 0.19},
    "1088.HK": {"name": "中國神華", "min_yield": 6.7, "golden_yield": 8.1, "max_pe": 10.0, "tax_rate": 0.10, "shares": 0, "manual_dps": 2.2389}
}

# ==========================================
# 3. 動態數據抓取 (混合智能股息 + 容錯機制)
# ==========================================
@st.cache_data(ttl=300)
def fetch_stock_market_data(ticker_code, retries=3):
    time.sleep(random.uniform(1.0, 3.0)) 
    
    for i in range(retries):
        try:
            ticker = yf.Ticker(ticker_code, session=session)
            fast_price = ticker.fast_info.get('lastPrice', 0)
            price = round(fast_price, 3)
            
            info = ticker.info
            pe = info.get('trailingPE', None)
            eps = info.get('trailingEps', None)
            
            # 智能股息抓取：交叉比對歷史與預測
            trailing_div = info.get('trailingAnnualDividendRate', 0)
            forward_div = info.get('dividendRate', 0)
            
            if forward_div and trailing_div:
                safe_div = min(forward_div, trailing_div)
                div_warning = "⚠️ 預警：市場預期減息" if forward_div < trailing_div * 0.9 else "✅ 派息穩定"
            else:
                safe_div = forward_div or trailing_div
                div_warning = "✅ 單一數據源"
            
            if price > 0:
                return {"price": price, "pe": pe, "eps": eps, "safe_div": safe_div, "div_warning": div_warning}
                
        except Exception:
            if i < retries - 1:
                time.sleep(random.uniform(3.0, 5.0))
                continue
            
            try:
                backup_price = round(yf.Ticker(ticker_code, session=session).fast_info.get('lastPrice', 0), 3)
                if backup_price > 0:
                    return {"price": backup_price, "pe": None, "eps": None, "safe_div": None, "div_warning": "🔴 網絡超時降級"}
            except:
                pass
                
    return None

market_data_cache = {}
with st.spinner('📡 雷達啟動中，正在掃描 100% 港股防禦水庫數據... (約需15-20秒)'):
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
    m_data = market_data_cache.get(ticker_code)
    if m_data is None or m_data["price"] == 0: continue
    
    current_price = m_data["price"]
    shares = config["shares"]
    
    # 決定使用自動抓取的保守股息，還是手動輸入的後備股息
    raw_dps = m_data.get("safe_div") if m_data.get("safe_div") else config["manual_dps"]
    net_dps = raw_dps * (1 - config["tax_rate"])
    
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
col1.metric(label="💰 500萬水庫當股市值 (100% 港股)", value=f"${total_market_value:,.2f}")
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
# 5. 📊 實時火控監測面版 (終極整合版)
# ==========================================
st.subheader("📊 實時火控監測面版")

for ticker_code, config in stocks_config.items():
    m_data = market_data_cache.get(ticker_code)
    
    if m_data is None or m_data["price"] == 0:
        st.error(f"❌ 網絡超時：無法獲取 {config['name']} ({ticker_code}) 數據。")
        continue
        
    current_price = m_data["price"]
    current_pe = m_data["pe"]
    eps = m_data["eps"]
    safe_div = m_data["safe_div"]
    div_warning = m_data.get("div_warning", "")
    
    # 決定使用自動抓取的保守股息，還是手動輸入的後備股息
    active_dps = safe_div if safe_div else config["manual_dps"]
    data_source_label = "智能抓取" if safe_div else "手動後備"
    
    # 計算實質息率
    net_dps = active_dps * (1 - config["tax_rate"])
    current_yield = (net_dps / current_price) * 100
    max_fire_price = net_dps / (config["min_yield"] / 100)
    
    # 🌟 派息比率健康檢查 (包含公用股白名單)
    payout_ratio_display = "暫無數據"
    payout_pass = True 
    is_utility = ticker_code in ['0002.HK', '1038.HK', '0006.HK']
    healthy_limit = 100 if is_utility else 75
    danger_limit = 120 if is_utility else 90

    if eps and eps > 0 and active_dps:
        payout_ratio = (active_dps / eps) * 100
        payout_ratio_display = f"{payout_ratio:.1f}%"
        if payout_ratio > danger_limit:
            payout_pass = False 
    elif eps is not None and eps <= 0:
        payout_ratio_display = "負盈利"
        payout_pass = False 
    
    # 三重條件判定 (股息、PE、派息比率)
    yield_pass = current_yield >= config["min_yield"]
    pe_pass = (current_pe is None) or (current_pe <= config["max_pe"])
    
    if yield_pass and pe_pass and payout_pass:
        status_icon = "🟢"
        is_green = True
    else:
        status_icon = "🔻"
        is_green = False
        premium = ((config["min_yield"] / current_yield) - 1) * 100 if current_yield > 0 else 0

    pe_display = f"{current_pe:.1f} 倍" if current_pe is not None else "暫無數據"
    expander_title = f"{status_icon} {config['name']} ({ticker_code}) - 現價: ${current_price:.2f} | 息率: {current_yield:.2f}% ({data_source_label}) | PE: {pe_display} | 派息比率: {payout_ratio_display}"
    
    with st.expander(expander_title, expanded=True):
        st.write(f"**防線設定：** 淺綠息率 {config['min_yield']:.1f}% | 上限 PE: {config['max_pe']:.1f}倍 | 派息比率紅線: {danger_limit}%")
        if "預警" in div_warning:
            st.warning(div_warning)
            
        if is_green:
            st.success(
                f"🍏 **全綠燈放行！** 息率達標 ({current_yield:.2f}%)、估值合理 ({pe_display})，且派息現金流健康 ({payout_ratio_display})。\n\n"
                f"**戰術：** 啟動常規步兵分批建倉（最高合理買入價 ${max_fire_price:.2f}）。"
            )
        else:
            if not payout_pass:
                st.error(
                    f"🚨 **派息崩塌預警！** 派息比率高達 {payout_ratio_display}，超越 {danger_limit}% 安全線！(可能正在消耗現金儲備派息)\n\n"
                    f"**戰術：** 絕對鎖死買入！若持有舊倉，強烈建議觀察下期財報，準備套現換馬！"
                )
            elif yield_pass and not pe_pass:
                st.warning(
                    f"⚠️ **高息估值陷阱！** 息率雖達標，但實時 PE ({pe_display}) 超過安全上限 {config['max_pe']:.1f} 倍。\n\n"
                    f"**戰術：** 拒絕開火，可能預期盈利將大幅倒退，繼續鎖死保險箱觀察！"
                )
            else:
                st.warning(
                    f"🔴 **股息率未達標！** 距離淺綠開火線尚有 **+{premium:.1f}%** 溢價（目標開火價 ${max_fire_price:.2f}）。\n\n"
                    f"**戰術：** 忍手！將子彈留給未來的特價區。"
                )

# UI 結尾留白
st.write("---")
st.caption("Powered by 終極 100% 港股防禦系統")
