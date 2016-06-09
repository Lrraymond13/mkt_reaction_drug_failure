import funcy
import numpy as np
from os.path import join
import pandas as pd
import cPickle as pickle
import string

EXPORT_DUPS = 1
DIR = '/Users/lrraymond13/MIT/'
COMP_TICKER_FNAME = 'company_names_to_8_cusips.csv'
comp_id_fname = 'output_companies_flat_all_new.csv'


# Define String Cleaning Function
def strip_upcase(str_var):
    str_v = str_var.strip().upper()
    return '_'.join(str_v.split())


def strip_punctuation(str_var):
    excluded_char = set(string.punctuation)
    str_split = ''.join('_' if ch in excluded_char else ch for ch in str_var)
    return '_'.join(str_split.split('_'))


def get_ticker(ticker, isin):
    # Ticker stored not only in ticker column, may be in ISIN instead
    # tickers are always < 10 char, so if not finding valid string in
    # ticker col, checks ISIN col, otherwise returns np.nan
    # okay if ticker numeric - may be listed overseas
    ticker_len = len(str(ticker))
    isin_len = len(str(isin))
    if ticker_len < 10:
        return ticker
    if isin_len < ticker_len:
        return isin
    return np.nan


def to_pickle(file, filename):
    dest = filename + '.p'
    file.to_pickle(dest)


def from_pickle(filename):
    source = filename + '.p'
    return pd.read_pickle(source)


def clean_get_df(comp_ticker_fname, cwd):
    # read in company names to cusips data set
    # strip/upcase comany name, convert cusips to numberical
    # change index to cleaned company name (this will be merge key)
    if not comp_ticker_fname:
        comp_ticker_fname = COMP_TICKER_FNAME
    if not cwd:
        cwd = DIR

    comp_ticker = pd.read_csv(join(cwd, comp_ticker_fname))
    comp_ticker['CLEAN_NAME'] = comp_ticker['Company name'].apply(strip_upcase)

    # clean and convert all column headers to upcase with _ delimiters
    clean_columns = funcy.rcompose(strip_upcase, strip_punctuation)
    comp_ticker.columns = list(map(clean_columns, comp_ticker.columns))

    # set index to be company name
    comp_ticker_sorted = comp_ticker.sort_values(['CLEAN_NAME', 'TICKER_SYMBOL'])
    # about 40 companies are duplicates - sort by ticker length and take one with shorter ticker
    dup_names = comp_ticker_sorted[comp_ticker_sorted.duplicated(['CLEAN_NAME'], keep=False)]
    if EXPORT_DUPS == 1:
        dup_names.to_csv(join(cwd, 'company_ticker_duplicates.csv'))

    comp_ticker_sorted['CLEAN_TICKER'] = comp_ticker_sorted.apply(
        lambda x: get_ticker(x['TICKER_SYMBOL'], x['ISIN_NUMBER']), axis=1)
    comp_ticker_dups = comp_ticker_sorted.drop_duplicates('CLEAN_NAME', keep='first')

    # convert cusips to integers
    bad_cusips = ('INVALID ISIN', 'INVALID', 'UNLISTED')
    replace_vals = (np.nan, np.nan, np.nan, np.nan)
    replace_dict = dict(zip(bad_cusips, replace_vals))
    comp_ticker_clean = comp_ticker_dups.replace({'9_DIGIT_CUSIP': replace_dict, '8_DIGIT_CUSIP': replace_dict})

    comp_ticker_clean[[
        'CLEAN_NAME', 'COMPANY_NAME', 'TICKER_SYMBOL', '9_DIGIT_CUSIP', '8_DIGIT_CUSIP', 'CLEAN_TICKER']
    ].set_index('CLEAN_NAME', verify_integrity=True, inplace=True)

    # pick file and export
    comp_ticker_clean.to_csv(join(cwd, 'company_ticker_clean.csv'))
    to_pickle(comp_ticker_clean, 'company_ticker_clean')
    return comp_ticker_clean

