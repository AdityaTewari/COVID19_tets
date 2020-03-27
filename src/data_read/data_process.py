import numpy as np


def country_sum(country_vals, first_non_zeros=None):
    country_vals = np.stack(country_vals, axis=0)
    return country_vals.sum(axis=0)


def diff_grad(series_val):
    ser_grad = np.zeros_like(series_val)
    ser_diff = series_val[1:] - series_val[:-1]
    ser_grad[1:] = ser_diff
    return ser_grad


def sort_series(series_data_list, data_title_list):
    series_last_vals = [series_data[-1] for series_data in series_data_list]
    series_sort_oder = np.argsort(series_last_vals)
    series_sort_oder = np.flip(series_sort_oder)
    data_title_list = [[data_title_list[j][i] for i in series_sort_oder] for j in range(len(data_title_list))]
    print(data_title_list)
    series_data_list = [series_data_list[i] for i in series_sort_oder]
    return series_data_list, data_title_list


def smoothen_gradien(gradient_val_list, mom=0.5):
    smoothed_grad = [0]*len(gradient_val_list)
    smoothed_grad[0] =  gradient_val_list[0]
    for j, gradient_val in enumerate(gradient_val_list[1:]):
        this_grad_val = (smoothed_grad[j]*mom + gradient_val)
        this_grad_val = this_grad_val/(1+mom)
        smoothed_grad[j+1] = this_grad_val
    return np.array(smoothed_grad)


def calc_gradients(country_series, edge_orders=1, grad_by_diff=False, smooth_grad=True):
    if grad_by_diff:
        first_gradient = diff_grad(country_series)
    else:
        first_gradient = np.gradient(np.array(country_series), edge_order=edge_orders)
    second_gradient = np.gradient(first_gradient)
    if smooth_grad:
        if not grad_by_diff:
            first_gradient = smoothen_gradien(first_gradient)
        second_gradient = smoothen_gradien(second_gradient)
    return first_gradient, second_gradient
