# -*- coding: utf-8 -*-
"""
生成HMM方法所需的数据格式的文件
"""


class hmm_training_data():
    """
        data_num : 表示一天记录数
        data_list : 记录列表,列表中的元素是字典｛time_field_segment：value,device_id=value,device_status=value｝
    """

    def __int__(self):
        data_num = 0
        data_list = list()
        feature_list = list()

    def add_data(self, time_field_segment_value, device_id_value, device_status_value):
        data_list.append({"time_field_segment": time_field_segment_value, "device_id": device_id_value, "device_status":
                         device_status_value})
        data_num += 1

    def
