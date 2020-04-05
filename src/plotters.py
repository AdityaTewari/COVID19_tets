import numpy as np
import matplotlib.pyplot as plt
from src.data_read import data_process
import os

def plot_covd_status(v_fit, model_data, v_time, model_time,  country_name, min_cases=1, plot_name="logistic",
                     plot_path=None):
    linewidth = 0.75
    plt.plot(v_time, v_fit, label="estimates")
    plt.plot(model_time, model_data, label="historical data", marker=".", linewidth=linewidth)
    plt.legend( loc='lower left')

    plt.xlabel('Days since {0} cases'.format(min_cases))
    plt.ylabel('Cases Expected')
    plt.title('The covid projection model for {}'.format(country_name))
    plt.grid(True)
    main_name = "projection_" + plot_name + ".png"
    if plot_path is not None:
        main_name = os.path.join(plot_path, main_name)
    plt.savefig(main_name)
    plt.close()
    # plt.show()


def plot_gradients(grads_lists, grad_axs=None, main_series=None, ax_main=None, count_start=0, linewidth=0.75):
    write_over = True
    plt.grid(True)
    if main_series is not None:
        if ax_main is None:
            fig_main = plt.figure()
            ax_main = fig_main.add_subplot(1, 1, 1)
        ax_main.plot(np.arange(count_start, len(main_series)+count_start), main_series,  marker=".", linewidth=linewidth)
    if grad_axs is None:
        grad_axs = [None, None]
        write_over = False
    for i, grads_list in enumerate(grads_lists):
        if write_over:
            ax = grad_axs[i]
        else:
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
        ax.plot(np.arange(count_start, len(grads_list)+count_start), grads_list, marker=".", linewidth=linewidth)
        grad_axs[i] = ax
    return ax_main, grad_axs


def plot_finalise(grad_fig_axs, fig_main_axs, data_names, x_label="days", plot_name="covid_gradient", plot_path=None,
                  is_ratio=False):
    grads_suffix = ["st", "nd", "rd", "th"]
    for i, ax in enumerate(grad_fig_axs):
        suff_count = i + 1
        suff_grad = grads_suffix[i] if suff_count < 3 else "th"
        legend = [str(suff_count) + suff_grad + " derivative in " + data_name for data_name in data_names]
        ax.set_xlabel(x_label)
        ax.set_ylabel('Cases')
        ax.set_title("Covid national gradients")
        ax.legend(legend)
        ax.grid(which='both', linestyle='--')
        ax.grid(which='minor', alpha=0.2)
        save_name = plot_name + str(i) + ".png"
        if plot_path is not None:
            save_name = os.path.join(plot_path, save_name)
        ax.figure.savefig(save_name)
        plt.close()
    if fig_main_axs is not None:
        fig_main_axs.set_xlabel(x_label)
        fig_main_axs.set_ylabel('Cases')
        if is_ratio:
            fig_main_axs.set_title("Covid national Infection Percentages")
            main_legend = ["cumulative %s " + data_name for data_name in data_names]
        else:
            fig_main_axs.set_title("Covid national Sums")
            main_legend = ["cumulative " + data_name for data_name in data_names]
        fig_main_axs.legend(main_legend)
        fig_main_axs.grid(which='both', linestyle='--')
        fig_main_axs.grid(which='minor', alpha=0.2)
        main_name = "main_" + plot_name  + ".png"
        if plot_path is not None:
            main_name = os.path.join(plot_path, main_name)
        fig_main_axs.figure.savefig(main_name)
    plt.close()


def plotter(covid_list, plot_name="covid_gradient", plot_path=None, data_name="country", last_n=None, min_case=0):
    figures = None
    start_index = np.where(covid_list > min_case)
    covid_list = covid_list[start_index[0][0]:]
    if last_n is None:
        x_label = 'Days Since {} cases reported'.format(min_case)
    else:
        x_label = 'Since {} days back'.format(last_n)
    first, second = data_process.calc_gradients(covid_list)
    fig_main, figures = plot_gradients([first, second], grad_axs=figures, main_series=covid_list, count_start=0)
    plot_finalise(figures, fig_main, [data_name], x_label=x_label, plot_name=plot_name, plot_path=plot_path)


def multi_country_plot(multi_country_data, first_non_zeros, data_title_list, plot_path=None,
                       plot_name="multi_country_covid", last_n=3650, lower_bound=1, grad_by_diff=True,
                       country_pops=None, smooth_grad=False):
    figures = None
    fig_main = None
    x_label = 'Days since {0} cases'.format(lower_bound)
    line_width = 0.5
    line_step = (2.0 - 0.5)/len(multi_country_data)
    if country_pops is not None:
        multi_country_data, group = data_process.sort_series(multi_country_data, [data_title_list, country_pops])
        data_title_list, country_pops = group[0], group[1]
    else:
        multi_country_data, group = data_process.sort_series(multi_country_data, [data_title_list])
        data_title_list = group[0]
    for i, (country_val, first_non_zero) in enumerate(zip(multi_country_data, first_non_zeros)):
        if country_pops is not None:
            country_pop = country_pops[i]
            country_val = np.divide(country_val, country_pop) * 100
        country_val = country_val[first_non_zero:]
        if last_n < len(country_val):
            country_val = country_val[-1 * last_n:]
            x_label = 'Since {} days back'.format(last_n)
        first, second = data_process.calc_gradients(country_val, grad_by_diff=grad_by_diff, smooth_grad=smooth_grad)
        fig_main, figures = plot_gradients([first, second], figures, main_series=country_val, ax_main=fig_main,
                                           count_start=0, linewidth=line_width + (i*line_step))
    if country_pops is not None:
        main_ratio = True
    else:
        main_ratio = False
    plot_finalise(figures, fig_main, data_title_list, x_label, plot_name=plot_name, plot_path=plot_path,
                  is_ratio=main_ratio)