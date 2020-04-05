from __future__ import division
from src.data_read import read_history, data_process
from src import plotters, models
from src.models import fit_functions
from scipy.optimize import curve_fit
import numpy as np
import datetime

funcs = [fit_functions.richard, fit_functions.logistic]


def average_model(x_vals, ts, norm_ts=None, ratio=True):
    func_i = 0
    ts.sort()
    if ratio and (norm_ts is not None):
        ts = ts / norm_ts
    while len(funcs) > func_i:
        try:
            popt, pcov = curve_fit(funcs[func_i], x_vals, ts)
            break
        except:
            func_i += 1
    if not(func_i < len(funcs)):
        return None
    else:
        return (popt, pcov), func_i


def fit_contry_models(country_names, covid_vals_list, popul_vals, first_non_zeros, plot_path=None,
                      data_kind="confirmed"):
    future_peak = 21
    lower_bound = 30
    ratio = True
    for i, country in enumerate(country_names):
        if covid_vals_list[i] is None:
            pass
        else:
            covid_vals = covid_vals_list[i][first_non_zeros[i]:]
            x_vals = np.arange(1, len(covid_vals)+1)
            fit_params = average_model(x_vals, covid_vals, popul_vals[i], ratio=ratio)
            if fit_params is not None:
                (popt, pconv), funcs_i = fit_params
                future_time = np.arange(1, len(x_vals) + future_peak)
                v_fit = funcs[funcs_i](future_time, *popt)
                if ratio:
                    v_fit = v_fit * popul_vals[i]
                plotters.plot_covd_status(v_fit, covid_vals, future_time, x_vals, country, min_cases=lower_bound,
                                          plot_name=country + "_" + data_kind, plot_path=plot_path)
            else:
                print("failed curve fit for the country {0} and datatype {1}".format(country, data_kind))


if __name__ == '__main__':
    date_today = datetime.datetime.now()
    date = date_today.strftime("%d_%m_%Y")
    country_name_list = models.country_names
    plot_path = models.plot_path
    import os
    date_folder = os.path.join(plot_path, date)
    lower_bound = 50
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)
    _, popul_vals = read_history.get_popu_lists(with_pop=True, subset_names=country_name_list)
    d_type = ["confirmed_global", "deaths_global"]
    lower_bounds = [30, 0]
    for data_kind, lower_bound in zip(d_type, lower_bounds):
        country_mat, first_non_zeros = read_history.read_country_mat(country_names=country_name_list, lower_bound=lower_bound,
                                                                     data_type=data_kind, moving_window=0)
        fit_contry_models(country_name_list, country_mat, popul_vals, first_non_zeros, plot_path=date_folder,
                          data_kind=data_kind)
    for data_kind, lower_bound in zip(d_type, lower_bounds):
        country_mat, first_non_zeros = read_history.read_country_mat(country_names=country_name_list, lower_bound=lower_bound,
                                                                     data_type=data_kind, moving_window=3)
        for plot_ratio in [True, False]:
            country_sum = data_process.country_sum(country_mat)
            if plot_ratio:
                country_pop = [100]*len(country_name_list)
                for j, country_name in enumerate(country_name_list):
                    try:
                        i = country_name_list.index(country_name)
                        country_pop[j] = popul_vals[i]
                    except ValueError:
                        country_pop[j] = None
            plotters.plotter(country_sum, plot_name="Sum_Plot", plot_path=date_folder, data_name="Sum of nations", min_case=lower_bound)
            if plot_ratio:
                plot_name = data_kind + "_" + "multicountry_ratio_"
                plotters.multi_country_plot(country_mat, first_non_zeros, data_title_list=country_name_list, plot_name=plot_name,
                                            plot_path=date_folder, lower_bound=lower_bound, country_pops=country_pop,
                                            smooth_grad=False)
            else:
                plot_name = data_kind + "_" + "multicountry_"
                plotters.multi_country_plot(country_mat, first_non_zeros, data_title_list=country_name_list, plot_name=plot_name,
                                            plot_path=date_folder, lower_bound=lower_bound, country_pops=None, smooth_grad=False)
        # country_names = european_list
