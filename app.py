import os
import sys
import time
import random

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

st.title("🎯 500萬水庫火控雷達 (9:1 終極退休陣型)")
st.markdown("**長倉必勝！舊倉看賣，新金買息。(智能「股息 + PE + 派息比率」三重火控版)**")
st.divider()

# ==========================================
# 2. 核心數據庫 (純手動精準派息 + 嚴格 PE 防線)
# ==========================================
stocks_config = {
    "0941.HK": {"name": "中移動", "min_yield": 5.8, "golden_yield": 6.7, "max_pe": 12.0, "tax_rate": 0.10, "shares": 500, "dps": 5.27},
    "0883.HK": {"name": "中海油", "min_yield": 6.3, "golden_yield": 7.6, "max_pe": 10.0, "tax_rate": 0.10, "shares": 5000, "dps": 1.28},
    "0002.HK": {"name": "中電", "min_yield": 4.5, "golden_yield": 5.5, "max_pe": 20.0, "tax_rate": 0.00, "shares": 1000, "dps": 3.20},
    "3988.HK": {"name": "中銀", "min_yield": 6.7, "golden_yield": 7.6, "max_pe": 6.0, "tax_rate": 0.10, "shares": 0, "dps": 0.2531},
    "1038.HK": {"name": "長建", "min_yield": 5.0, "golden_yield": 6.0, "max_pe": 16.0, "tax_rate": 0.00, "shares": 0, "dps": 2.61},
    "0005.HK": {"name": "滙控", "min_yield": 6.5, "golden_yield": 7.5, "max_pe": 10.0, "tax_rate": 0.00, "shares": 0, "dps": 5.857},
    "1883.HK": {"name": "CTM", "min_yield": 7.5, "golden_yield": 8.5, "max_pe": 15.0, "tax_rate": 0.00, "shares": 0, "dps": 0.19},
    "1088.HK": {"name": "中國神華", "min_yield": 6.7, "golden_yield": 8.1, "max_pe": 10.0, "tax_rate": 0.10, "shares": 0, "dps": 2.2389}
}

# ==========================================
# 3. 動態數據抓取 (人類行為模擬 + 降級容錯機制)
# ==========================================
@st.cache_data(ttl=300)
def fetch_stock_market_data(ticker_code, retries=3):
    # 加入隨機休眠，模擬人類逐隻股票 Click 入去睇嘅節奏 (1至3秒)
    time.sleep(random.uniform(1.0, 3.0)) 
    
    for i in range(retries):
        try:
            ticker = yf.Ticker(ticker_code)
            
            # 1. 先用 fast_info 鎖定最基本嘅現價 (呢個極少被 Block)
            fast_price = ticker.fast_info.get('lastPrice', 0)
            price = round(fast_price, 3)
            
            # 2. 嘗試獲取深入財務數據 (.info 容易被 Block)
            info = ticker.info
            pe = info.get('trailingPE', None)
            eps = info.get('trailingEps', None)
            yf_dps = info.get('trailingAnnualDividendRate', None)
            
            if price > 0:
                return {"price": price, "pe": pe, "eps": eps, "yf_dps": yf_dps}
                
        except Exception:
            if i < retries - 1:
                # 俾人 Block 咗，扮死停耐啲 (3至5秒) 再試
                time.sleep(random.uniform(3.0, 5.0))
                continue
            
            # 如果真係拎唔到深入數據，降級處理：只回傳現價，PE/EPS 當無數據
            try:
                backup_price = round(yf.Ticker(ticker_code).fast_info.get('lastPrice', 0), 3)
                if backup_price > 0:
                    return {"price": backup_price, "pe": None, "eps": None, "yf_dps": None}
            except:
                pass
                
    return None

# 預先加載所有市場數據 (包含 QQQ)
market_data_cache = {}
with st.spinner('📡 雷達啟動中，正在隱蔽掃描市場數據... (約需15-20秒)'):
    for ticker_code in list(stocks_config.keys()) + ["QQQ"]:
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
col1.metric(label="💰 港股防禦盾市值 (90%)", value=f"${total_market_value:,.2f}")
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
# 5. 📊 實時火控監測面版 (引入 PE 與派息比率安全鎖)
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
    yf_dps = m_data["yf_dps"]
    
    # 計算實質息率
    net_dps = config["dps"] * (1 - config["tax_rate"])
    current_yield = (net_dps / current_price) * 100
    max_fire_price = net_dps / (config["min_yield"] / 100)
    
    # 🌟 派息比率健康檢查
    payout_ratio_display = "暫無數據"
    payout_pass = True # 預設放行
    is_utility = ticker_code in ['0002.HK', '1038.HK', '0006.HK']
    healthy_limit = 100 if is_utility else 75
    danger_limit = 120 if is_utility else 90

    if eps and eps > 0 and yf_dps:
        payout_ratio = (yf_dps / eps) * 100
        payout_ratio_display = f"{payout_ratio:.1f}%"
        if payout_ratio > danger_limit:
            payout_pass = False # 觸發危險紅燈
    elif eps is not None and eps <= 0:
        payout_ratio_display = "負盈利"
        payout_pass = False # 虧損公司不買
    
    # 🌟 核心修訂：三重條件判定 (股息、PE、派息比率)
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
    expander_title = f"{status_icon} {config['name']} ({ticker_code}) - 現價: ${current_price:.2f} | 息率: {current_yield:.2f}% | PE: {pe_display} | 派息比率: {payout_ratio_display}"
    
    with st.expander(expander_title, expanded=True):
        st.write(f"**防線設定：** 淺綠息率 {config['min_yield']:.1f}% | 上限 PE: {config['max_pe']:.1f}倍 | 派息比率紅線: {danger_limit}%")
        
        if is_green:
            st.success(
                f"🍏 **全綠燈放行！** 息率達標 ({current_yield:.2f}%)、估值合理 ({pe_display})，且派息現金流健康 ({payout_ratio_display})。\n\n"
                f"**戰術：** 啟動常規步兵分批建倉（最高合理買入價 ${max_fire_price:.2f}）。"
            )
        else:
            # 區分開火失敗的原因
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

st.divider()

# ==========================================
# 6. 🚀 衛星增長引擎 (10% 預算定投 QQQ)
# ==========================================
st.subheader("🚀 衛星增長引擎 (10% IB 美股碎股定投)")
qqq_data = market_data_cache.get("QQQ")

if qqq_data and qqq_data["price"] > 0:
    qqq_price = qqq_data["price"]
    monthly_budget_hkd = 4000
    monthly_budget_usd = monthly_budget_hkd / 7.8 # 粗略匯率
    est_shares = monthly_budget_usd / qqq_price
    
    st.info(
        f"**納斯達克 100 指數 ETF (QQQ)**\n\n"
        f"🦅 **實時現價：** ${qqq_price:.2f} USD\n\n"
        f"📊 **本月執行指令：** 不看估值、不看股息。使用本月 10% 預算 (約 $512 USD)，於每月 26 號透過 IB 買入約 **{est_shares:.3f} 股**。"
    )
else:
    st.error("暫時無法獲取 QQQ 實時數據，請稍後重試。")
