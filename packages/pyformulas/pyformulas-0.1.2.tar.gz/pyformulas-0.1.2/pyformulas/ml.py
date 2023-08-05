def do_standardization(X):
    from tensorflow import log, zeros_like, where

    standardized = where(X > zeros_like(X), X+log(X+1), X-log(-X+1))

    return standardized

#def do_standardization(x):
#    if x > 0:
#        return x + np.log(x + 1)
#    else:
#        return x - np.log(-x + 1)
#
#do_standardization = np.vectorize(do_standardization)