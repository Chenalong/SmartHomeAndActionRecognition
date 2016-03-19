# -*- coding: utf-8 -*-

import codecs
import os
import numpy as np

from CreateHmmTrainingData import hmm_training_data
from DataReader import obtain_time_disperse_degree
from DataReader import date_format
from DataReader import obtain_time_disperse_degree
from DataReader import obtain_id_for_action
from DataReader import format_data_reader
from DataReader import obtain_action_name
from sklearn.datasets.base import Bunch
from sklearn import tree
from sklearn.externals.six import StringIO


class decision_tree_feature:
    # 提取的特征放在该变量中
    training_data = []
    training_target = []

    def __int__(self):
        pass

    def format_weekday(self, weekday):
        if weekday < 6:
            return 1
        return 0

    def add_data(self, record):
        weekday_feature = self.format_weekday(record['week'])
        action_id = record['device_id'] * 2 + record['device_status']
        time_field_feature = record['time_field_segment']
        season_feature = record['season']
        self.training_data.append((weekday_feature, time_field_feature, season_feature))
        self.training_target.append(action_id)

    def extract_features(self,hmm_model):
        format_data_list = format_data_reader()
        for record in format_data_list:
            self.add_data(record)

        for date in hmm_model.date_2_feature_dict:
            for index, action in enumerate(hmm_model.date_2_feature_dict[date]):
                if action == 0:
                    week = (date - 16850 + 4) % 7 + 1
                    week = self.format_weekday(week)
                    if date >= 16861:
                        season = 1
                    else:
                        season = 4
                    self.training_data.append((week,index,season))
                    self.training_target.append(0)

    def load_smart_home_data(self):
        n_samples = len(self.training_data)
        n_features = len(self.training_data[0])
        target_names = np.array(obtain_action_name())
        data = np.empty((n_samples, n_features))
        target = np.empty((n_samples,), dtype=np.int)
        for i in range(n_samples):
            data[i] = np.asarray(self.training_data[i], dtype=np.int)
            target[i] = np.asarray(self.training_target[i], dtype=np.int)




        return Bunch(data=data, target=target,
                     target_names=target_names,
                     DESCR="SmartHomeAndActionRecognition",
                     feature_names=['is_weekday', 'time_field_segment',
                                    'season'])




