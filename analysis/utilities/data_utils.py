import csv
import funcy
import string
import xlrd


def clean_unicode(string_entry):
    try:
        return unicode(string_entry).encode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        string_entry.decode('utf-8', 'replace').encode('utf-8')


# Define String Cleaning Function
def filter_str(var):
    str_var = str(var)
    printable_chars = set(string.printable)
    return ''.join(filter(lambda x: x in printable_chars, str_var))


def strip_upcase(str_var):
    delim = '_'
    str_v = str(str_var).strip().upper()
    res = delim.join(str_v.split())
    # strip first and last _ chars
    if res[0] == delim:
        res = res[1:]
    if res[-1] == res:
        res = res[:-1]
    return res


def strip_punctuation(str_var):
    excluded_char = set(funcy.concat(string.punctuation, ['@']))
    str_split = ''.join('_' if ch in excluded_char else ch for ch in str_var)
    return '_'.join(str_split.split('_'))


# Define column cleaning function
clean_columns = funcy.compose(strip_upcase, strip_punctuation, filter_str)


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
    # remove unicode and convert random txt files to csv delimited clean versions
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




