import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

def simulate_assets(start_year, start_age, initial_assets, annual_return, monthly_investment, end_investment_year, start_withdrawal_year, withdrawal_rate):
    end_year = start_year + (100 - start_age)
    years = list(range(start_year, end_year + 1))
    ages = list(range(start_age, 101))
    
    assets = [initial_assets]
    monthly_withdrawals = [0]
    
    for year in years[1:]:
        prev_asset = assets[-1]
        current_asset = prev_asset
        
        for month in range(12):
            if year <= end_investment_year:
                current_asset += monthly_investment
            monthly_return = (1 + annual_return) ** (1/12) - 1
            current_asset *= (1 + monthly_return)
            if year >= start_withdrawal_year:
                monthly_withdrawal = prev_asset * withdrawal_rate / 12
                current_asset -= monthly_withdrawal
            else:
                monthly_withdrawal = 0
        
        assets.append(max(0, current_asset))
        if year >= start_withdrawal_year:
            monthly_withdrawals.append(prev_asset * withdrawal_rate / 12)
        else:
            monthly_withdrawals.append(0)
            
    results = pd.DataFrame({
        '西暦': years,
        '年齢': ages,
        '投資資産額': assets,
        '毎月の取り崩し金額': monthly_withdrawals
    })
    return results

def plot_simulation(results):
    fig, ax1 = plt.subplots(figsize=(12, 8))
    
    ax1.set_xlabel('Age', fontsize=12)
    ax1.set_ylabel('Total Assets (10,000 JPY)', fontsize=12)
    ax1.plot(results['年齢'], results['投資資産額'] / 10000, 'b-', linewidth=2)
    ax1.tick_params(axis='y', labelcolor='blue')
    
    def millions_formatter(x, pos):
        return f'{x:.0f}'
    ax1.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Monthly Withdrawal (10,000 JPY)', fontsize=12, color='red')
    ax2.plot(results['年齢'], results['毎月の取り崩し金額'] / 10000, 'r-', linewidth=2)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    
    plt.title('Asset Balance and Monthly Withdrawal by Age', fontsize=16)
    ax1.legend(['Total Assets'], loc='upper left')
    ax2.legend(['Monthly Withdrawal'], loc='upper right')
    plt.tight_layout()
    
    return fig

def format_currency(value):
    return f"{value:,.0f}"

# --- Streamlit アプリケーション ---
st.title('「じぶん年金」シミュレーション')

# サイドバー入力
with st.sidebar:
    st.header('入力パラメータ')
    start_year = st.number_input('開始年（西暦）', min_value=2000, max_value=2100, value=2025)
    start_age = st.number_input('年齢', min_value=20, max_value=90, value=30)
    initial_assets = st.number_input('保有している投資資産（円）', min_value=0, value=5000000)
    annual_return = st.slider('年間利回り（%）', min_value=0.0, max_value=15.0, value=7.0) / 100
    monthly_investment = st.number_input('毎月の積立額（円）', min_value=0, value=30000)
    end_investment_year = st.number_input('積立終了年（西暦）', min_value=start_year, max_value=2100, value=start_year + 30)
    start_withdrawal_year = st.number_input('取り崩し開始年（西暦）', min_value=start_year, max_value=2100, value=start_year + 35)
    withdrawal_rate = st.slider('年間取り崩し率（%）', min_value=0.0, max_value=10.0, value=4.0) / 100

# --- シミュレーション実行 ---
if st.sidebar.button('シミュレーション実行'):
    results = simulate_assets(
        start_year,
        start_age,
        initial_assets,
        annual_return,
        monthly_investment,
        end_investment_year,
        start_withdrawal_year,
        withdrawal_rate
    )

    st.markdown(
        """
        <style>
        div[data-testid="stDataEditor"] thead th {
            text-align: center;
        }
        div[data-testid="stDataEditor"] tbody td {
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.header('「投資資産」と「取り崩し金額」の推移')
    fig = plot_simulation(results)
    st.pyplot(fig)

    st.header('シミュレーション結果')

    # 金額整形
    display_results = results.copy()
    #display_results['投資資産額'] = display_results['投資資産額'].apply(format_currency)
    #display_results['毎月の取り崩し金額'] = display_results['毎月の取り崩し金額'].apply(format_currency)


    # --- テーブル表示 ---
    st.data_editor(
        display_results,
        hide_index=True,
        column_config={
            "投資資産額": st.column_config.NumberColumn("投資資産額", format="%d", width="medium", disabled=True),
            "毎月の取り崩し金額": st.column_config.NumberColumn("毎月の取り崩し金額", format="%d", width="medium", disabled=True),
            "西暦": st.column_config.NumberColumn("西暦", format="%d", width="small", disabled=True),
            "年齢": st.column_config.NumberColumn("年齢", format="%d", width="small", disabled=True)
        }
    )

    # --- CSVダウンロード ---
    csv = results.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="CSVファイルをダウンロード",
        data=csv,
        file_name='asset_projection_results.csv',
        mime='text/csv',
    )

else:
    st.info('左側のパラメータを設定し、「シミュレーション実行」ボタンをクリックしてください。')
