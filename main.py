import os

import pandas as pd
import streamlit as st
import numpy as np
from bs4 import BeautifulSoup
import urllib.request as ur
import re

# Enter a stock symbol
from src.pl_scrapper import get_pl_csv

# index = 'AMBUJACEM.NS'
# # URL link
# url_bs = 'https://in.finance.yahoo.com/quote/' + index + '/balance-sheet?p=' + index
# url_cf = 'https://in.finance.yahoo.com/quote/' + index + '/cash-flow?p=' + index
from src.visualizer import plot

plot = st.cache(plot)


def main():
    st.title('**Exploring Financial Data**')
    tickers = [x + '.NS' for x in pd.read_csv('data/NSE_equity.csv')['SYMBOL'].to_list()]
    # tickers = ['ULTRACEMCO.NS', 'SHREECEM.NS', 'AMBUJACEM.NS', 'ACC.NS', 'RAMCOCEM.NS', 'BIRLACORPN.NS', 'INDIACEM.NS',
    #            'DALBHARAT.NS', 'ORIENTCEM.NS', 'HEIDELBERG.NS']
    pl_cols = get_pl_csv(tickers[0]).columns
    with st.sidebar:
        st.title('Filter')
        tckrs_to_show = st.multiselect('Stock Tickers', tickers)
        cols_to_show = st.multiselect('Income statement features', pl_cols)

    if len(cols_to_show) > 0:
        failed_tckrs = set()
        for col in cols_to_show:
            df_data = {}
            for tckr in tckrs_to_show:
                try:
                    pl = get_pl_csv(tckr)
                    df_data[tckr] = pl[col]
                except:
                    failed_tckrs.add(tckr)

            df = pd.DataFrame(df_data)
            st.plotly_chart(plot(df, col))
        if len(failed_tckrs) > 0:
            st.write(f'Failed to load these stocks: {failed_tckrs}')
    else:
        st.write('Select a feature and a tckr from the sidebar to show to get started')


if __name__ == '__main__':
    main()
