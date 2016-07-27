import csv
import funcy
import numpy as np
import string
import xlrd


DELIM = '_'

def clean_unicode(string_entry):
    try:
        return unicode(string_entry).encode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        string_entry.decode('utf-8', 'replace').encode('utf-8')


# Define String Cleaning Function
def strip_upcase(str_var):
    str_v = str(str_var).strip().upper()
    res = DELIM.join(str_v.split())
    # strip first and last _ chars
    if res[0] == DELIM:
        res = res[1:]
    if res[-1] == res:
        res = res[:-1]
    return DELIM.join(filter(None, res.split(DELIM)))


def strip_punctuation(str_var):
    excluded_char = set(string.punctuation) - set([DELIM])
    if not isinstance(str_var, str):
        print(str_var)
        return str_var
    return ''.join(ch for ch in str_var if ch not in excluded_char)


def remove_stopwords(str, stopwords, DELIM='_'):
    if not isinstance(stopwords, set):
        stopwords = set(stopwords)
    newstr = filter(lambda x: x not in stopwords, str.split(DELIM))
    return DELIM.join(newstr)

# Define column cleaning function
clean_columns = funcy.rcompose(strip_punctuation, strip_upcase)


def csv_from_excel(filename, csv_filename=None):
    # converts .xls files to csv, clean unicode issues
    wb = xlrd.open_workbook(''.join([str(filename), '.xls']))
    sheets = wb.sheet_names()
    if not csv_filename:
        csv_filename = filename
    with open(''.join([str(csv_filename), '.csv']), 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        for sheet in sheets:
            wsheet = wb.sheet_by_name(sheet)
            for rownum in xrange(wsheet.nrows):
                writer.writerow([clean_unicode(entry) for entry in wsheet.row_values(rownum)])


def csv_from_txt(txt_filename, csv_filename=None):
    # remove unicode and convert random txt files to csv DELIMited clean versions
    if not csv_filename:
        csv_filename = txt_filename

    with open(csv_filename, 'wb') as f:
        writer = csv.writer(f)
        with open(txt_filename, 'r') as t:
            dialect = csv.Sniffer().sniff(t.read(1024))
            t.seek(0)
            rdr = csv.reader(t, delimiter=dialect.delimiter, quoting=csv.QUOTE_MINIMAL)
            for line in rdr:
                writer.writerow([clean_unicode(entry) for entry in line])




