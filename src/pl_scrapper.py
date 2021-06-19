import os

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import urllib.request as ur
import re


def get_pl_csv(tckr):
    data_dir = 'data'
    if not os.path.exists(f'{data_dir}/{tckr}_pl.csv'):
        new_ls = scrape_pl(tckr)

        pl = create_df(new_ls)
        pl.to_csv(f'{data_dir}/{tckr}_pl.csv')

    pl = pd.read_csv(f'{data_dir}/{tckr}_pl.csv', index_col=0)
    pl = reformat_df(pl)
    pl = add_req_cols(pl)
    cols_to_show = ['Total revenue', 'Cost of revenue', 'Gross profit', 'Gross Profit Margin',
                    'Total operating expenses', 'Operating P/L % Gross Profit', 'Operating income or loss',
                    'Interest expense', 'Interest Expense % Op P/L', 'Income before tax', 'Income tax expense',
                    'Income Tax % Op P/L', 'Net Earnings', 'Net Earnings % Revenue', 'Diluted E.P.S.',
                    'Selling general and administrative', 'Selling general and administrative % Gross Profit']
    pl = pl[cols_to_show]
    pl.columns = [x.title() for x in pl.columns]
    return pl


def add_req_cols(pl):
    pl = pl.copy()
    pl['Gross Profit Margin'] = pl['Gross profit'] * 100 / pl['Total revenue']
    pl['Selling general and administrative % Gross Profit'] = pl['Selling general and administrative'] * 100 / pl[
        'Gross profit']
    pl['Operating P/L % Gross Profit'] = pl['Operating income or loss'] * 100 / pl['Gross profit']
    pl['Interest Expense % Op P/L'] = pl['Interest expense'] * 100 / pl['Operating income or loss']
    pl['Income Tax % Op P/L'] = pl['Income tax expense'] * 100 / pl['Operating income or loss']
    pl['Net Earnings'] = pl['Net income']
    pl['Net Earnings % Revenue'] = pl['Net Earnings'] * 100 / pl['Total revenue']
    pl['Diluted E.P.S.'] = pl['Net Earnings'] / pl['Diluted average shares']
    pl['Basic E.P.S.'] = pl['Net Earnings'] / pl['Basic average shares']
    pl.loc[np.isinf(pl['Diluted E.P.S.']), 'Diluted E.P.S.'] = np.nan
    pl.loc[np.isinf(pl['Basic E.P.S.']), 'Basic E.P.S.'] = np.nan
    return pl


def reformat_df(pl):
    pl = pl.replace(to_replace='-', value='0')
    for col in pl.columns:
        try:
            pl[col] = pl[col].str.replace(',', '')
        except AttributeError as e:
            if str(e) == 'Can only use .str accessor with string values!':
                pass
            else:
                raise e
        finally:
            pl[col] = pl[col].astype(np.float32)
    return pl


def create_df(new_ls):
    pl = pd.DataFrame(new_ls[1:])
    pl.columns = new_ls[0]  # Name columns to first row of dataframe
    pl = pl.T
    pl.columns = pl.iloc[0]  # Name columns to first row of dataframe
    pl.drop(pl.index[0], inplace=True)  # Drop first index row
    pl.index.name = ''  # Remove the index name
    pl.drop('ttm', axis=0, inplace=True)
    return pl


def scrape_pl(tckr):
    url_is = 'https://in.finance.yahoo.com/quote/' + tckr + '/financials?p=' + tckr
    read_data = ur.urlopen(url_is).read()
    soup_is = BeautifulSoup(read_data, 'lxml')
    ls = [l.string for l in soup_is.find_all('span')]
    new_ls = list(filter(None, ls))
    splits = [i for i, x in enumerate(new_ls) if bool(re.match(r'[a-zA-Z\s]+', x))]
    tmp = [new_ls[:splits[0]]]
    for prev_s, curr_s in zip(splits, splits[1:]):
        tmp.append(new_ls[prev_s:curr_s])
    new_ls = tmp + new_ls[curr_s:splits[-1]]
    new_ls = list(filter(lambda x: len(x) > 1, new_ls))
    for i, x in enumerate(new_ls):
        if x[0] == 'ttm':
            break
    new_ls = new_ls[i:-1]
    new_ls[0].insert(0, 'Breakdown')
    max_len = len(max(new_ls[:-1], key=len))
    for i, x in enumerate(new_ls[1:]):
        while len(x) < max_len:
            x.insert(1, '-')
        new_ls[i + 1] = x
    return new_ls
