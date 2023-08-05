import csv

from qa.utils import get_variable_writer


INFILE = 'variables.csv'
OUTFILE = 'variables_uniquefied.csv'

"""
A problem has crept in whereby some rows are repeated with different ordering. Remove them. 
"""

reader = csv.DictReader(open(INFILE))
dict = {}
key_array = []

count = 0
for row in reader:
    try:
        dict[row['xpath']]
    except KeyError:
        key_array.append(row['xpath'])


    print("row is %s" % row)
    count += 1
    dict[row['xpath']] = row

keys = 0
for key in key_array:
    print dict[key]
    keys += 1

headers = ['parent_sked','parent_sked_part', 'in_a_group','db_table','ordering','db_name','xpath','irs_type','db_type','line_number','description','versions']


writer = get_variable_writer(OUTFILE)
for key in key_array:           
        writer.writerow(dict[key])

print ("count %s keys %s\nheaders: %s" % (count, keys, headers))

