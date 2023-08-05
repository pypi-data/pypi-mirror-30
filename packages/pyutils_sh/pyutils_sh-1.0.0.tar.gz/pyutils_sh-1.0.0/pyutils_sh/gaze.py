import numpy as np


def cross_correlation(person1, person2, framerate=25, constrain_seconds=2):
    """
     - This function takes 2 lists/arrays of data and calculates the normalized max cross-correlation value with its associated lag.
     - Additionally, it will also return the cross-correlation value at 0 lag, as well as the entire normalized array as a python list.
     - You can manually set the time constraints by changing the variable values.
 
    negative lag means person2 lags behind person1 by x frames
    e.g.
    A = [0,1,2,3,0,0,0]
    B = [0,0,0,1,2,3,0]
    cross_correlation(A,B)


    positive lag means person1 lags behind person2 by x frames
    e.g.
    A = [0,0,0,1,2,3,0]
    B = [0,1,2,3,0,0,0]
    cross_correlation(A,B)
    """

    # convert lists to numpy arrays
    x = np.array(person1)
    y = np.array(person2)

    # calculate cross correlation values
    correlations = np.correlate(x, y, 'full')

    # trim the cross-correlation values to a range (-lag_limits : +lag_limits)
    # trim AFTER cross correlation calculation to avoid 0 padding of signals
    # assumes x and y are equal length
    lag_limits = constrain_seconds*framerate
    trimmed_correlations = correlations[len(x)-1-lag_limits:len(x)+lag_limits]

    # normalize the cross-correlation values for ease of comparison between
    # subjects
    norm_array = trimmed_correlations / (np.linalg.norm(x) * np.linalg.norm(y))

    # get maximum normalized cross-correlation value
    max_R = max(norm_array)
    
    # get lag of max correlation value
    max_lag = np.argmax(norm_array)

    # trimmed array is now 2*(lag_limits)+1 elements long
    # adjust it so that lag 0 is a complete match
    max_lag_adj = max_lag - lag_limits

    # Get the normalized zero lag correlation value
    zero_R = norm_array[lag_limits]

    # returns (max cross correlation, lag of max correlation), 0 lag
    # correlation, the entire normalized array
    return (float(max_R), float(max_lag_adj), float(zero_R), norm_array.tolist())
