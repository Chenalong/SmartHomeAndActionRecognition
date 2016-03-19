# -*- coding: utf-8 -*-
"""
这个文件负责数据的读取和对缺失数据的填补和处理，并返回一个列表，每个列表中的元素是一个字典，字典形式如下所示：
｛'week':5,'device_location':'bedroom','season':4,'device_status':1,'device_name':'light','days_after_1970':16850,'time_field_segment':15,'device_id':7｝

"""

import os
import codecs
import ConfigParser
import datetime


def obtain_data_path():
    config = ConfigParser.ConfigParser()
    config.read('ConfigFile.txt')
    return config.get("DataPath", "path")


def obtain_time_disperse_degree():
    config = ConfigParser.ConfigParser()
    config.read('ConfigFile.txt')
    return config.get("TimeDisperseDegree", "length")


def obtain_id_for_action(id):
    config = ConfigParser.ConfigParser()
    config.read('ConfigFile.txt')
    return config.get("id_action", str(id))


def obtain_action_num():
    config = ConfigParser.ConfigParser()
    config.read('ConfigFile.txt')
    return config.get("action_num", 'num')

def obtain_action_name():
    config = ConfigParser.ConfigParser()
    config.read('ConfigFile.txt')
    action_num = int(obtain_action_num())
    action_name_list = []
    for i in range(action_num):
        if i == 1 or i == 4 or i == 5:
            continue
        action_name_list.append(obtain_id_for_action(i))
    return action_name_list

def process_data_file(file_path, data_list):
    file_read = codecs.open(file_path, "r")
    for line in file_read:
        data_list.append(line.strip())
    file_read.close()


def data_clean(data_list):
    """
        去除列标题行和空行
    """

    for line in data_list:
        if line.startswith(('1', '2', '3''4', '5', '6', '7', '8', '9', '0')) is False:
            data_list.remove(line)
            continue
        if line.startswith(','):
            data_list.remove(line)
            continue


def cal_date_diff(date_str):
    tmp_str = date_str.split('/')
    year = int(tmp_str[0])
    month = int(tmp_str[1])
    day = int(tmp_str[2])
    date_1970 = datetime.datetime(1970, 1, 1)
    date_now = datetime.datetime(year, month, day)
    return (date_now - date_1970).days


def date_format(date):
    date_1970 = datetime.datetime(1970, 1, 1)
    date_now = date_1970 + datetime.timedelta(days=date)
    return str(date_now)


def change_season_to_num(season_str):
    if season_str == "spring":
        return 1
    if season_str == "summer":
        return 2
    if season_str == "fall":
        return 3
    if season_str == "winter":
        return 4


def change_status_to_binary(device_status_str):
    if device_status_str == "OFF":
        return 0
    return 1


def data_transformation(data):
    field_array = data.split(',')
    if len(field_array) != 8:
        return None
    data_dic = {}
    date_time_str = field_array[1]
    date_str = date_time_str.split()[0]
    time_str = date_time_str.split()[1]
    data_dic['days_after_1970'] = cal_date_diff(date_str)
    time_disperse_degree = int(obtain_time_disperse_degree())
    data_dic['time_field_segment'] = (int(time_str.split(':')[0]) * 60 + int(
        time_str.split(':')[1])) / time_disperse_degree
    data_dic['week'] = int(field_array[2])
    data_dic['season'] = change_season_to_num(field_array[3])
    data_dic['device_location'] = field_array[4]
    data_dic['device_name'] = field_array[5]
    if field_array[6] == '':
        data_dic['device_id'] = -1
    else:
        data_dic['device_id'] = int(field_array[6])
    data_dic['device_status'] = change_status_to_binary(field_array[7])
    return data_dic


def data_format(data_list):
    """
        格式化后的数据每条记录都是以字典的形式保存在format_data_list 列表中
    """
    format_data_list = list()
    for line in data_list:
        format_data_list.append(data_transformation(line))

    return format_data_list


def data_reader():
    path_string = obtain_data_path()
    data_list = list()
    for root, dirs, files in os.walk(path_string):
        for file_name in files:
            if file_name.endswith(".csv"):
                process_data_file(os.path.join(root, file_name), data_list)
    return data_list


def data_fill(format_data_list):
    """
    对数据中某些记录中设备唯一标识符列为空的情况下进行填补
    """
    device_name_2_id = {}
    for record in format_data_list:
        if record['device_id'] != -1:
            device_name_2_id[(record['device_location'], record['device_name'])] = record['device_id']

    for record in format_data_list:
        if record['device_id'] == -1:
            record['device_id'] = device_name_2_id[(record['device_location'], record['device_name'])]


def format_data_reader():
    data_list = data_reader()
    data_clean(data_list)
    format_data_list = data_format(data_list)
    data_fill(format_data_list)
    write_format_data_2_file(format_data_list)
    return format_data_list


def write_format_data_2_file(format_data_list):
    file_write = codecs.open("format_file.txt", "w")
    for record in format_data_list:
        file_write.writelines(str(record))
        file_write.writelines('\n')
    file_write.close()


# if __name__ == '__main__':
# format_data_list = format_data_reader()
#     # write_format_data_2_file(format_data_list)
