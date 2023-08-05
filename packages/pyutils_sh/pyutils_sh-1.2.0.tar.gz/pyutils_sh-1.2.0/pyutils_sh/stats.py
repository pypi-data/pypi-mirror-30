"""
Tools for calculating different types of statistics, such as effect size 
estimates.
"""

import numpy as np


def cohens_d(g1_m, g1_sd, g1_n, g2_m, g2_sd, g2_n):
    """
    Calculate Cohen's d for two independent samples.
    
    This calculation involves taking the mean difference between groups, and 
    dividing it by the pooled standard deviation.

    Parameters
    ----------
    g1_m : float
        Mean value for group 1.
    g1_sd : float
        Standard deviation for group 1.
    g1_n : int
        Sample size of group 1.
    g2_m : float
        Mean value for group 2.
    g2_sd : float
        Standard deviation for group 2.
    g2_n : int
        Sample size of group 2.

    Returns
    -------
    d : float
        Standardized effect size (Cohen's d) for the group difference.
    """

    mean_diff = g2_m - g1_m
    
    sd_num = ((g1_n - 1)*np.square(g1_sd)) + ((g2_n - 1)*np.square(g2_sd))
    sd_denom = g1_n + g2_n - 2
    
    sd_pooled = np.sqrt(sd_num / sd_denom)
    
    return mean_diff/sd_pooled
