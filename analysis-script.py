#!/bin/python
import codecs
import json

sim_dict = {}
mis_dict = {}


def parse_input(path_eng):
    dict = {}
    with codecs.open(path_eng, 'r', 'utf-16') as txt_file:
        for row in txt_file:
            if len(row.rstrip()) != 0:
                row_arr = row.strip().split(',')
                dict[row_arr[0]] = row_arr[1]

    return dict


def write_dict_to_csv(dict, path):
    with open(path, 'w') as file:
        file.write(json.dumps(dict))


def add_count_to_dict(dict, key):
    if key not in dict:
        dict[key] = 1;
    else:
        dict[key] = dict[key] + 1


def calc_cs_wise_report(sim_dict, mis_dict):
    dict_final = {}
    dict_final['SIMILARITY'] = {}
    dict_final['MISMATCH'] = {}
    for key in dict_final:
        dict_used = {}
        dict_in = {}
        if key == 'SIMILARITY':
            dict_used = sim_dict
        else:
            dict_used = mis_dict
        for k, value in dict_used.items():
            value = eval(value)
            if 0 <= value < 0.1:
                add_count_to_dict(dict_in, '0.0')
            elif 0.1 <= value < 0.2:
                add_count_to_dict(dict_in, '0.1')
            elif 0.2 <= value < 0.3:
                add_count_to_dict(dict_in, '0.2')
            elif 0.3 <= value < 0.4:
                add_count_to_dict(dict_in, '0.3')
            elif 0.4 <= value < 0.5:
                add_count_to_dict(dict_in, '0.4')
            elif 0.5 <= value < 0.6:
                add_count_to_dict(dict_in, '0.5')
            elif 0.6 <= value < 0.7:
                add_count_to_dict(dict_in, '0.6')
            elif 0.7 <= value < 0.8:
                add_count_to_dict(dict_in, '0.7')
            elif 0.8 <= value < 0.9:
                add_count_to_dict(dict_in, '0.8')
            elif 0.9 <= value < 1.0:
                add_count_to_dict(dict_in, '0.9')
            elif value == 1.0:
                add_count_to_dict(dict_in, '1.0')

        dict_final[key] = dict_in
    return dict_final


def process():
    folder = '30-35'
    sim_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result' + '\\' + folder + '\\' + 'similarity.txt'
    mis_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result' + '\\' + folder + '\\' + 'mismatch.txt'
    result_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result' + '\\' + folder + '\\' + 'analysis.txt'
    sim_dict = parse_input(sim_path)
    mis_dict = parse_input(mis_path)
    final_dict = calc_cs_wise_report(sim_dict, mis_dict)
    write_dict_to_csv(final_dict, result_path)


process()



