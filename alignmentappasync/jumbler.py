import codecs
import csv
import random

two_files = True
file_encoding = 'utf-16' \
                ''


def parse_input_file(path_eng, path_indic):
    source = []
    target_corp = []
    if two_files:
        with codecs.open(path_eng, 'r', file_encoding) as txt_file:
            for row in txt_file:
                if len(row.rstrip()) != 0:
                    source.append(row.rstrip())
        with codecs.open(path_indic, 'r', file_encoding) as txt_file:
            for row in txt_file:
                if len(row.rstrip()) != 0:
                    target_corp.append(row.rstrip())

    else:
        with codecs.open(path_eng, 'r', file_encoding) as csv_file:
            csv_reader = csv.reader((l.replace('\0', '') for l in csv_file))
            for row in csv_reader:
                if len(row) != 0:
                    source.append(row[0])
                    target_corp.append(row[1])
    return source, target_corp

def jumble(list):
    new_list = random.sample(list, len(list))
    return new_list

def write_output(list, path):
    with codecs.open(path, 'w', file_encoding) as txt_file:
        for row in list:
            txt_file.write(row + "\r\n")

def process():
    path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\length-wise\5000\src-ik-en.txt'
    path_indic = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\length-wise\5000\target-ik-hi.txt'
    output_src = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\length-wise\5000\jumbled\src.txt'
    output_trgt = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\length-wise\5000\jumbled\trgt.txt'
    src, trgt = parse_input_file(path, path_indic)
    write_output(jumble(src), output_src)
    write_output(jumble(trgt), output_trgt)
    print("Done.")


process()
