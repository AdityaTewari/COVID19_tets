import pandas as pd
import numpy as np
from src.data_read import  data_path, time_series_path, ts_file_name

import os


def read_full_file(data_type="confirmed_global"):
    file_name = ts_file_name + data_type + ".csv"
    file_path = os.path.join(os.path.join(data_path, time_series_path), file_name)
    df = pd.read_csv(file_path)
    i = df.drop(columns=[ "Lat", "Long"])
    return i

# def get_country_list(country_list=None):
#     data_frame = read_full_file()
#     if country_list is None:
#         country_list = list(set(data_frame["Country/Region"].tolist()))
#     for country_name in country_list:
#         k = data_frame[data_frame[data_frame["Country/Region"]==country_name].columns[2:]].sum(axis=1)
#     return country_list
#     # print(country_list, data_frame)


def get_country_list(data_frame=None):
    if data_frame is None:
        data_frame = read_full_file()
    country_list = list(set(data_frame["Country/Region"].tolist()))
    return country_list


def make_country_df(data_frame):
    country_list = get_country_list(data_frame)
    countries = []
    countries_cost = []
    for country_name in country_list:
        k = data_frame[data_frame["Country/Region"] == country_name].sum(axis=0, skipna = True, numeric_only=True)
        countries.append(country_name)
        countries_cost.append(k.tolist())
    countries_cost = np.array(countries_cost)
    return {"countries": countries, "countries_cost": countries_cost}


def get_popu_lists(with_pop=False, subset_names = None):
    csv_file = "/home/aditya/PYTHON_PROJECTS/personal_projects/COVID19_tets/src/models/pop_data.csv"
    df = pd.read_csv(csv_file)
    names = df["name"].to_list()
    if with_pop:
        popul = df["pop2020"].to_list()
    else:
        popul = None
    if subset_names is not None:
        pop_dict = dict(zip(names, popul))
        popul = [pop_dict[name] for name in subset_names]
        names = subset_names
    return names, popul


def read_country_data(country_names, lower_bound=0, data_type="confirmed_global"):
    country_id = -1
    data_frame = read_full_file(data_type=data_type)
    country_dict = make_country_df(data_frame)
    first_non_zeros = []
    country_case_lists = []
    for country_name in country_names:
        for i, country in enumerate(country_dict["countries"]):
            if country == country_name:
                country_id = i
                break
        country_cases_list = country_dict["countries_cost"][country_id, :]
        # read_country = read_country[ 2:]
        # start_val = country_cases_list[0]
        read_country = [read_country_val for read_country_val in country_cases_list]
        first_non_zero = -1
        for en, t in enumerate(read_country):
            if t > lower_bound:
                first_non_zero = en
                break
        if first_non_zero == -1:
            print("no covid in {} yet".format(country_name))
            first_non_zero = 0
        country_case_lists.append(country_cases_list[:]), first_non_zeros.append(first_non_zero)
    return country_case_lists, first_non_zeros


def worst_yet(country_dict, top_n=10 ):
    today_stat = country_dict["countries_cost"][:, -1]
    todays_worst_index = list(np.argsort(-1 * today_stat))[:top_n]
    return  todays_worst_index


if __name__ == '__main__':
    data_frame = read_full_file()
    country_dict = make_country_df(data_frame)
