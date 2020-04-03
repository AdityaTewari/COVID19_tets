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

    result = (1 + beta * np.exp(-1 * rate * x_val))

    result = result ** (1 / slope)
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


def average_model(top_n=10):
    data_frame = read_history.read_full_file()
    country_dict = read_history.make_country_df(data_frame)
    todays_worst_index = read_history.worst_yet(country_dict, top_n=top_n)
    todays_worst = [country_dict["countries"][i] for i in todays_worst_index]
    future_peak = 21
    func = logistic
    lower_bound = 10
    guess = None
    for country in todays_worst:
        covid_vals = read_history.read_country_data(country, lower_bound=lower_bound)
        print(covid_vals)
        if covid_vals is None:
            pass
        else:
            covid_vals = list(set(covid_vals))
            covid_vals.sort()
            time_scale = np.arange(1, len(covid_vals)+1)
            print(country, " ------------------------------------ ")
            popt, pcov = curve_fit(func, time_scale, covid_vals)
            print(popt, pcov)
            future_time = np.arange(1, len(time_scale) + future_peak)
            v_fit = func(future_time, *popt)
            plotters.plot_covd_status(v_fit, covid_vals, future_time, time_scale, country, min_cases=lower_bound)


if __name__ == '__main__':
    plot_path = "D:\personal\PROJECTS\COVID_spread_modetl\src\plot_models"
    d_type = ["confirmed_global", "deaths_global"]
    average_model(top_n=10)
    for data_kind in d_type:
        for plot_ratio in [True, False]:
            lower_bound = 30
            european_list, pop = read_history.european_countries(with_pop=True)
            print(european_list)
            country_vals, _ = read_history.read_country_data(country_names=european_list, lower_bound=0, data_type=data_kind)
            europe_sum = data_process.country_sum(country_vals)
            country_names = ["Italy", "Netherlands", "Spain", "Germany", "United Kingdom"]
            if plot_ratio:
                country_pop = [100]*len(country_names)
                for j, country_name in enumerate(country_names):
                    try:
                        i = european_list.index(country_name)
                        country_pop[j] = pop[i]
                    except ValueError:
                        pass
            date_today = datetime.datetime.now()
            date = date_today.strftime("%d_%m_%Y")
            import os
            date_folder = os.path.join(plot_path, date)
            if not os.path.exists(date_folder):
                os.makedirs(date_folder)
            country_mat, first_non_zeros = read_history.read_country_data(country_names=country_names, lower_bound=lower_bound, data_type=data_kind)
            country_mat = np.array(country_mat)
            moving_window = 5
            country_mat_new =country_mat
            for i in range(1, moving_window):
                country_mat_new[:, i:] = country_mat_new[:, :-1*i] + country_mat[:, i:]
            plotters.plotter(europe_sum, plot_name="Europe", plot_path=date_folder, data_name="Europe", min_case=lower_bound)
            if plot_ratio:
                plot_name = date + "_" + data_kind + "_" + "multicountry_ratio_"
                plotters.multi_country_plot(country_mat, first_non_zeros, data_title_list=country_names, plot_name=plot_name,
                                            plot_path=date_folder, lower_bound=lower_bound, country_pops=country_pop,
                                            smooth_grad=False)
            else:
                plot_name = date + "_" + data_kind + "_" + "multicountry_"
                plotters.multi_country_plot(country_mat, first_non_zeros, data_title_list=country_names, plot_name=plot_name,
                                            plot_path=date_folder, lower_bound=lower_bound, country_pops=None, smooth_grad=False)
        # country_names = european_list
