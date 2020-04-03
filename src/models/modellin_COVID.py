from __future__ import division
from src.data_read import read_history, data_process
from src import plotters
from scipy.optimize import curve_fit
import numpy as np
import datetime

def richard(x_val, alpha, beta, rate, slope):
    """
    Computes the Richard growth model
    Parameters
    ----------
    time : time
    alpha : upper asymptote
    beta : growth range
    rate : growth rate
    slope : slope of growth
    See Also
    --------
    richard_inverse
    References
    ----------
    .. [1] D. Fekedulegn, M. Mac Siurtain, and J. Colbert, "Parameter estimation
           of nonlinear growth models in forestry," Silva Fennica, vol. 33, no.
           4, pp. 327-336, 1999.
    """
    eph = 0.00001
    result = (1 + beta * np.exp(-1 * rate * x_val))
    result = result ** (1 / (slope+eph))
    result = alpha / result
    return result


def logistic(x_val, alpha, beta, rate):
    """
    Computes the Logistic growth model
    Parameters
    ----------
    time : time
    alpha : upper asymptote
    beta : growth range
    rate : growth rate
    See Also
    --------
    logistic_inverse, generalised_logistic, generalised_logistic_inverse
    References
    ----------
    .. [1] D. Fekedulegn, M. Mac Siurtain, and J. Colbert, "Parameter estimation
           of nonlinear growth models in forestry," Silva Fennica, vol. 33,
           no. 4, pp. 327-336, 1999.
    """
    result = alpha / (1 + beta * np.exp(-1 * rate * x_val))
    return result



def exponential(t, a, b, alpha):
    return a - b * np.exp(alpha * t)




def average_model(country_names=None, top_n=10, plot_path=None):
    data_frame = read_history.read_full_file()
    country_dict = read_history.make_country_df(data_frame)
    if country_names is None:
        todays_worst_index = read_history.worst_yet(country_dict, top_n=top_n)
        country_names = [country_dict["countries"][i] for i in todays_worst_index]
    future_peak = 21
    func = richard
    lower_bound = 100
    guess = None
    covid_vals_list, first_non_zeros = read_history.read_country_data(country_names, lower_bound=lower_bound)
    _, popul_vals = read_history.get_popu_lists(with_pop=True, subset_names=country_names)
    print(covid_vals_list, popul_vals)
    for i, country in enumerate(country_names):
        if covid_vals_list[i] is None:
            pass
        else:
            covid_vals = covid_vals_list[i][first_non_zeros[i]:]
            # covid_vals = list(set(covid_vals))
            covid_vals.sort()
            covid_vals = covid_vals/popul_vals[i]
            time_scale = np.arange(1, len(covid_vals)+1)
            try:
                popt, pcov = curve_fit(func, time_scale, covid_vals)

                future_time = np.arange(1, len(time_scale) + future_peak)
                v_fit = func(future_time, *popt)
                plotters.plot_covd_status(v_fit, covid_vals, future_time, time_scale, country, min_cases=lower_bound,
                                          plot_name=country, plot_path=plot_path)
            except:
                print("failed curve fit for the country ".format(country))




if __name__ == '__main__':
    date_today = datetime.datetime.now()
    date = date_today.strftime("%d_%m_%Y")
    country_names = ["Italy", "India", "Spain", "Germany", "France"]
    plot_path = "/home/aditya/PYTHON_PROJECTS/personal_projects/COVID19_tets/src/plot_models"
    import os
    date_folder = os.path.join(plot_path, date)
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)
    average_model(country_names=country_names, top_n=5, plot_path=date_folder)
    d_type = ["confirmed_global", "deaths_global"]
    lower_bounds = [30, 0]
    for data_kind, lower_bound in zip(d_type, lower_bounds):
        for plot_ratio in [True, False]:
            european_list, pop = read_history.get_popu_lists(with_pop=True)
            print(european_list)
            country_vals, _ = read_history.read_country_data(country_names=european_list, lower_bound=0, data_type=data_kind)
            europe_sum = data_process.country_sum(country_vals)
            if plot_ratio:
                country_pop = [100]*len(country_names)
                for j, country_name in enumerate(country_names):
                    try:
                        i = european_list.index(country_name)
                        country_pop[j] = pop[i]
                    except ValueError:
                        pass
            country_mat, first_non_zeros = read_history.read_country_data(country_names=country_names, lower_bound=lower_bound, data_type=data_kind)
            plotters.plotter(europe_sum, plot_name="Europe", plot_path=date_folder, data_name="Europe", min_case=lower_bound)
            if plot_ratio:
                plot_name = data_kind + "_" + "multicountry_ratio_"
                plotters.multi_country_plot(country_mat, first_non_zeros, data_title_list=country_names, plot_name=plot_name,
                                            plot_path=date_folder, lower_bound=lower_bound, country_pops=country_pop,
                                            smooth_grad=False)
            else:
                plot_name = data_kind + "_" + "multicountry_"
                plotters.multi_country_plot(country_mat, first_non_zeros, data_title_list=country_names, plot_name=plot_name,
                                            plot_path=date_folder, lower_bound=lower_bound, country_pops=None, smooth_grad=False)
        # country_names = european_list
