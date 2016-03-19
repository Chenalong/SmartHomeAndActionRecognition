# -*- coding: utf-8 -*-
"""
生成HMM方法所需的数据格式的文件
"""
import codecs

from DataReader import obtain_time_disperse_degree
from DataReader import format_data_reader
from DataReader import date_format
from math import sqrt


class hmm_training_data:
    """
    data_num : 表示一天记录数
    date_2_data_dict : 是一个以时间为key的字典，字典元素为一个列表，列表中的元素是一个字典｛time_field_segment：value,device_id=value,device_status=value｝
    date_2_feature_dict: 是根据用户一天的行为，把它转换成一个24 * 60 /TimeDisperseDegree.length 向量
    """
    data_num = 0
    date_2_data_dict = dict()
    date_2_feature_dict = dict()
    lamba = 0

    def __init__(self, _lamba):
        self.lamba = _lamba

    def add_data(self, date_value, time_field_segment_value, device_id_value, device_status_value):
        if (date_value in self.date_2_data_dict) is False:
            self.date_2_data_dict[date_value] = list()

        self.date_2_data_dict[date_value].append(
            {"time_field_segment": time_field_segment_value, "device_id": device_id_value, "device_status":
                device_status_value})
        self.data_num += 1

    def load_format_data(self):
        format_data_list = format_data_reader()
        for item in format_data_list:
            self.add_data(item['days_after_1970'], item['time_field_segment'], item['device_id'], item['device_status'])
        print len(self.date_2_data_dict)


    def create_date_2_feature_dict(self):
        for date in self.date_2_data_dict:
            self.date_2_feature_dict[date] = [0] * (24 * 60 / int(obtain_time_disperse_degree()))
            for item in self.date_2_data_dict[date]:
                action_id = item['device_id'] * 2 + item['device_status']
                self.date_2_feature_dict[date][item['time_field_segment']] = action_id

    def download_feature_2_file(self):
        file_name = obtain_time_disperse_degree() + "_period_to_feature_for_date.txt"
        file_write = codecs.open(file_name, "w")
        for date in self.date_2_feature_dict:
            file_write.writelines(date_format(date).split()[0] + ": 的特征如下\n")
            for i in range((24 * 60 / int(obtain_time_disperse_degree()))):
                file_write.write(str(self.date_2_feature_dict[date][i]) + " ")
            file_write.writelines("\n")
        print "successed complete feature extract"
        file_write.close()

    def cal_sim_with_pierson(self, ori_date, test_date):
        x = self.date_2_feature_dict[ori_date]
        y = self.date_2_feature_dict[test_date]
        n = len(x)
        demo = 0
        dumo = 0
        for i in range(n):
            if x[i] != 0:
                demo += 1
        for i in range(n):
            if x[i] != 0 and x[i] == y[i]:
                dumo += 1
        # print "demo is %d and dumo is%d " % (demo, dumo)
        return dumo * 1.0 / demo

    def find_training_data_with_pierson(self, date):
        tmp_trainning_data = []
        for test_date in self.date_2_feature_dict:
            if test_date != date:
                pierson_sim = self.cal_sim_with_pierson(date, test_date)
                if pierson_sim > self.lamba:
                    tmp_trainning_data.append(self.date_2_feature_dict[test_date])
        print "in CreateHmmTrainingDate.py find_training_data_with_pierson() %d" % (len(tmp_trainning_data))
        return tmp_trainning_data
