import csv
import xlrd


def clean_unicode(string_entry):
    try:
        return unicode(string_entry).encode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        string_entry.decode('utf-8', 'replace').encode('utf-8')


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


def csv_from_txt(filename, csv_filename=None, delim='|'):
    # remove unicode and convert random txt files to csv delimited clean versions
    if not csv_filename:
        csv_filename = filename

    with open(''.join([str(csv_filename), '.csv']), 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        with open(''.join([str(filename), '.txt']), 'r') as r:
            for line in r.readlines():
                writer.writerow([clean_unicode(entry) for entry in line.split(delim)])


