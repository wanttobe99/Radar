import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. 介面基礎設定 (適應 iPhone 螢幕)
st.set_page_config(page_title="八大金剛 - 長倉必勝火控雷達", layout="wide", initial_sidebar_state="collapsed")
st.title("🛡️ 500萬水庫火控雷達")
st.markdown("**長倉必勝！舊倉看賣，新金買息。**")

# 2. 核心數據庫 - 八大金剛全陣容
# 預期派息 (expected_dps) 為近期大約數值，統帥可日後隨公司公佈自行微調
stocks_config = {
    # 👑 優先核心 (五大龍頭)
    "0941.HK": {"name": "中移動", "min_yield": 6.5, "golden_yield": 7.5, "max_pe": 12, "expected_dps": 4.83, "tax_rate": 0.10, "shares": 500}, 
    "0883.HK": {"name": "中海油", "min_yield": 6.0, "golden_yield": 8.0, "max_pe": 10, "expected_dps": 1.45, "tax_rate": 0.10, "shares": 5000},
    "0002.HK": {"name": "中電",   "min_yield": 4.2, "golden_yield": 5.0, "max_pe": 20, "expected_dps": 3.10, "tax_rate": 0.00, "shares": 1000},
    "3988.HK": {"name": "中銀",   "min_yield": 7.0, "golden_yield": 8.5, "max_pe": 6,  "expected_dps": 0.26, "tax_rate": 0.10, "shares": 0},
    "1038.HK": {"name": "長建",   "min_yield": 4.8, "golden_yield": 6.0, "max_pe": 15, "expected_dps": 2.56, "tax_rate": 0.00, "shares": 0},
    
    # ⚔️ 次選奇兵 (三大新血)
    "1088.HK": {"name": "神華",   "min_yield": 7.5, "golden_yield": 9.5, "max_pe": 10, "expected_dps": 2.40, "tax_rate": 0.10, "shares": 0},
    "0005.HK": {"name": "滙控",   "min_yield": 6.5, "golden_yield": 8.0, "max_pe": 12, "expected_dps": 4.75, "tax_rate": 0.00, "shares": 0},
    "1883.HK": {"name": "CTM",    "min_yield": 8.0, "golden_yield": 9.5, "max_pe": 10, "expected_dps": 0.245, "tax_rate": 0.00, "shares": 0}
}

# 3. 獲取實時數據 (使用緩存機制加速)
@st.cache_data(ttl=60) # 60秒刷新一次
def fetch_data():
    results = {}
    total_val = 0.0
    total_div = 0.0
    
    for ticker, info in stocks_config.items():
        try:
            stock = yf.Ticker(ticker)
            price = stock.fast_info.get('last_price', 0.0)
            if price == 0: price = stock.info.get('regularMarketPrice', 0.0)
            pe = stock.info.get('trailingPE', 0.0) or 0.0
        except:
            price, pe = 0.0, 0.0
            
        net_dps = info["expected_dps"] * (1 - info["tax_rate"])
        market_value = info["shares"] * price
        est_div = info["shares"] * net_dps
        net_yield = (net_dps / price * 100) if price > 0 else 0.0
        
        total_val += market_value
        total_div += est_div
        
        results[ticker] = {
            "代號": ticker,
            "股名": info["name"],
            "持股": info["shares"],
            "現價": price,
            "市值": market_value,
            "淨落袋息率": net_yield,
            "預計年股息": est_div,
            "淺綠線": info["min_yield"],
            "深綠線": info["golden_yield"],
            "稅後DPS": net_dps
        }
    return results, total_val, total_div

data, total_value, total_div = fetch_data()

# 4. 戰略大盤看板
st.subheader("大盤看板")
col1, col2, col3 = st.columns(3)
col1.metric("總持倉市值", f"${total_value:,.2f}")
col2.metric("預計年淨股息", f"${total_div:,.2f}")
col3.metric("平均每月被動收入", f"${(total_div/12):,.2f}")

# 5. 持倉統計表
st.subheader("部隊持倉統計")
df = pd.DataFrame.from_dict(data, orient='index')
display_df = df[["代號", "股名", "持股", "現價", "市值", "淨落袋息率", "預計年股息"]].copy()
display_df["現價"] = display_df["現價"].apply(lambda x: f"${x:.2f}")
display_df["市值"] = display_df["市值"].apply(lambda x: f"${x:,.2f}")
display_df["預計年股息"] = display_df["預計年股息"].apply(lambda x: f"${x:,.0f}")
display_df["淨落袋息率"] = display_df["淨落袋息率"].apply(lambda x: f"{x:.2f}%")
st.dataframe(display_df, use_container_width=True, hide_index=True)

# 6. 智能火控雷達分析
st.subheader("📡 彩色雷達戰術指令")
for ticker, info in data.items():
    with st.expander(f"{info['股名']} ({ticker}) - 現價: ${info['現價']:.2f} | 息率: {info['淨落袋息率']:.2f}%", expanded=True):
        st.write(f"**防禦設定：** 淺綠線 {info['淺綠線']}% | 深綠黃金線 {info['深綠線']}%")
        
        target_buy_price = info["稅後DPS"] / (info["淺綠線"] / 100) if info["淺綠線"] > 0 else 0.0
        
        if info['現價'] == 0:
            st.error("🔴 網絡錯誤，無法獲取報價。")
        elif info['淨落袋息率'] >= info['深綠線']:
            st.success(f"🟢 **深綠燈！** 突破 {info['深綠線']}% 黃金線！極端超值！\n\n**戰術：** 解鎖 29 萬戰備金，動用單發重炮無情轟炸！")
        elif info['淨落袋息率'] >= info['淺綠線']:
            st.info(f"🍏 **淺綠燈！** 進入常規伏擊圈 (最高開火價 ${target_buy_price:.2f})。\n\n**戰術：** 配合每月出糧資金，啟動常規步兵分批建倉。")
        else:
            diff_pct = ((info['現價'] - target_buy_price) / target_buy_price) * 100 if target_buy_price > 0 else 0
            st.warning(f"🔴 **紅燈！** 距離淺綠開火線尚有 +{diff_pct:.1f}% 溢價。\n\n**戰術：** 忍手！保險箱鎖死，將子彈留給未來的特價區。")

st.markdown("---")
st.caption("系統時間：實時同步 | 長倉必勝，紀律為王。")
