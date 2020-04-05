import numpy as np


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


def logistic(x_val, alpha, beta, rate, slope=None):
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


def exponential(t, a, b, alpha, slope=None):
    return a - b * np.exp(alpha * t)
