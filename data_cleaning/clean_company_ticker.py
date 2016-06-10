import funcy
import numpy as np
from os.path import join
import pandas as pd
import string

EXPORT_DUPS = 1
DIR = '/Users/lrraymond13/MIT/'
COMP_TICKER_FNAME = 'company_names_to_8_cusips'
COMP_ID_FNAME = 'output_companies_flat_all_new'


# Define String Cleaning Function
def strip_upcase(str_var):
    str_v = str(str_var).strip().upper()
    printable_chars = set(string.printable)
    filter_chars = ''.join(filter(lambda x: x in printable_chars, str_v))
    return '_'.join(filter_chars.split())


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


def get_clean_compticker_df(comp_ticker_fname, cwd):
    # read in company names to cusips data set
    # strip/upcase comany name, convert cusips to numberical
    # change index to cleaned company name (this will be merge key)
    if not comp_ticker_fname:
        comp_ticker_fname = COMP_TICKER_FNAME
    if not cwd:
        cwd = DIR

    comp_ticker = pd.read_csv(join(cwd, comp_ticker_fname + '.csv'))
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


def get_clean_compdrug_df(comp_drug_fname, cwd):
    # read in company names to cusips data set
    # strip/upcase comany name, convert cusips to numberical
    # change index to cleaned company name (this will be merge key)
    if not comp_drug_fname:
        comp_drug_fname = COMP_ID_FNAME
    if not cwd:
        cwd = DIR

    comp_id = pd.read_csv(join(DIR, comp_drug_fname + '.csv'), names=map(str, xrange(10)))
    comp_id_df = comp_id[['0', '1', '2']]
    del comp_id
    comp_id_df.columns = ['DRUG_ID', 'COMPANY_NAME', 'ANCESTOR']
    comp_id_df['CLEAN_NAME'] = comp_id_df['COMPANY_NAME'].apply(strip_upcase)
    comp_id_sorted = comp_id_df.sort_values(['CLEAN_NAME', 'DRUG_ID'], axis=0)

    dup_names = comp_id_sorted[comp_id_sorted.duplicated(['CLEAN_NAME'], keep=False)]
    dup_names.to_csv(join(DIR, 'company_id_duplicates.csv'))
    comp_id_dups = comp_id_sorted.drop_duplicates('CLEAN_NAME', keep='first')
    comp_d_df = comp_id_dups.set_index(['CLEAN_NAME'], verify_integrity=True)
    comp_d_df.to_csv(join(cwd, COMP_ID_FNAME + '.csv'))
    to_pickle(comp_d_df, COMP_ID_FNAME)
    return comp_d_df


def merge_drug_ticker(comp_ticker, comp_d_df):
    # inner merge of dataframes of company, ticker and company drug, merge on index
    merged = pd.merge(comp_ticker, comp_d_df, how='inner', left_index=True, right_index=True)
    unmatched = comp_ticker[(comp_ticker.CLEAN_TICKER != 'Unlisted') & (
        ~comp_ticker.CLEAN_TICKER.isin(merged[merged['CLEAN_TICKER'] != 'Unlisted'].CLEAN_TICKER))]
    unmatched_clean = unmatched.dropna()
    unmatched_clean.to_csv(join(DIR, 'Unmatched_listed_companies.csv'))
    merged.to_csv(join(DIR, 'company_drugids_ticker' + '.csv'))
    merged.to_pickle(join(DIR, 'company_drugids_ticker' + '.p'))
    return merged

