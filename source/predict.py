# -*- coding: utf-8 -*-
import codecs
import os
import sys
import pydot
import graphviz

from sklearn import tree
from CreateHmmTrainingData import hmm_training_data
from DataReader import obtain_time_disperse_degree
from DataReader import date_format
from DataReader import obtain_time_disperse_degree
from DataReader import obtain_action_num
from extract_feature_for_decision_tree import decision_tree_feature
from sklearn.externals.six import StringIO


def cal_precision(origin_action_list, predict_action_list):
    same_num = 0
    for i in range(len(origin_action_list)):
        if origin_action_list[i] == predict_action_list[i]:
            same_num += 1
    return same_num * 1.0 / len(origin_action_list)


def write_result_to_file(origin_action_list, predict_action_list, precison, file_dir, file_name):
    if os.path.exists(file_dir) is False:
        os.makedirs(file_dir)
    file_write = codecs.open(os.path.join(file_dir,file_name), "w")

    # 把预测结果写入文件中
    for ori in origin_action_list:
        file_write.writelines("%-4s" % (str(ori)))
    file_write.writelines("\n")

    for pre in predict_action_list:
        file_write.writelines("%-4s" % (str(pre)))
    file_write.writelines("\n")

    file_write.writelines("The correct ratio is " + str(precison))
    file_write.close()


def predict_by_hmm(hmm_model, date):
    # 获取训练数据
    trainning_data = hmm_model.find_training_data_with_pierson(date)
    action_num = int(obtain_action_num())
    origin_action_list = hmm_model.date_2_feature_dict[date]
    predict_action_list = [0] * len(origin_action_list)
    for i in range(len(origin_action_list)):
        num = [0] * action_num
        for item in trainning_data:
            num[item[i]] += 1
        max_freq = 0
        index = 0
        for j in range(action_num):
            if num[j] > max_freq:
                max_freq = num[j]
                index = j
            elif num[j] == max_freq:
                index = j
        predict_action_list[i] = index

    precison = cal_precision(origin_action_list, predict_action_list)
    module_path = os.path.dirname(__file__)

    file_name = "hmm_model_predict_in_" + date_format(date).split()[0] + ".txt"
    write_result_to_file(origin_action_list, predict_action_list, precison, os.path.join(module_path, "hmm_result"),
                         file_name)


def format_weekday(weekday):
    if weekday < 6:
        return 1
    return 0


def create_decision_tree_model():
    decision_tree_model = decision_tree_feature()
    decision_tree_model.extract_features(hmm_model)
    smart_home_data = decision_tree_model.load_smart_home_data()
    clf = tree.DecisionTreeClassifier()
    clf.fit(smart_home_data.data, smart_home_data.target)
    # 数据缓存变量
    dot_data = StringIO()
    # 把树模型信息以dot格式输出到dot_data变量中
    tree.export_graphviz(clf, out_file=dot_data,
                         feature_names=smart_home_data.feature_names,
                         class_names=smart_home_data.target_names,
                         filled=True, rounded=True,
                         special_characters=True)
    # 把dot格式的数据转变成graph格式的数据
    graph = pydot.graph_from_dot_data(dot_data.getvalue())
    # 通过Graphviz executor 把graph转换成pdf文档  在转换之前要手动安装Graphviz 该安装包可以在Graphviz官网下载
    graph.write_pdf('smart_home_data.pdf')
    return clf


def predict_by_decision_tree(hmm_model, decision_tree_model, date):
    origin_action_list = hmm_model.date_2_feature_dict[date]
    test_data = []
    time_field_segment = len(origin_action_list)
    for i in range(time_field_segment):
        week = (date - 16850 + 4) % 7 + 1
        week = format_weekday(week)
        if date >= 16861:
            season = 1
        else:
            season = 4
        test_data.append([week, i, season])
    predict_action_list = decision_tree_model.predict(test_data)
    precision = cal_precision(origin_action_list, predict_action_list)
    print "in %d days precision is %lf" % (date, precision)
    file_name = "decision_tree_model_predict_in_" + date_format(date).split()[0] + ".txt"
    module_path = os.path.dirname(__file__)
    write_result_to_file(origin_action_list, predict_action_list, precision,
                         os.path.join(module_path, "decision_tree_result"), file_name)


def create_hmm_model(lamba):
    """
    根据该日期对应的特征向量，根据皮尔逊相似度计算公式找寻相似特征的日期数据进行训练
    """
    # 生成一个隐马尔可夫模型的数据对象，该对象的变量date_2_data_dict存储了所需数据的格式
    hmm_model = hmm_training_data(lamba)
    # 数据加载
    hmm_model.load_format_data()
    # 为每天创建特征向量
    hmm_model.create_date_2_feature_dict()
    # 特征向量本地化
    # hmm_training_data.download_feature_2_file()
    return hmm_model


if __name__ == '__main__':
    # 创建一个hmm模型，传递一个lamba参数，这是选取相似数据的超参数
    hmm_model = create_hmm_model(0.5)
    # 对最后一周进行预测
    for i in range(7):
        predict_by_hmm(hmm_model, 16873 + i)

    # 下面是用决策树对用户的行为进行预测
    decision_tree_model = create_decision_tree_model()
    for i in range(7):
        predict_by_decision_tree(hmm_model, decision_tree_model, 16873 + i)






