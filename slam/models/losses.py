from keras import backend as K


def mean_squared_error(y_true, y_pred, scale=1.):
    return K.mean(K.square(y_pred[:, :1] * scale - y_true[:, :1] * scale), axis=-1)


def mean_absolute_error(y_true, y_pred, scale=1.):
    return K.mean(K.abs(y_pred[:, :1] * scale - y_true[:, :1] * scale), axis=-1)


def confidence_error(y_true, y_pred, scale=1., mode='log_std'):
    sigma = y_pred[:, 1] * scale

    delta = K.abs(y_true[:, 0] - y_pred[:, 0]) * scale # absolute error

    if mode == 'log_std': # negative log likelihood
        return K.mean(sigma + 0.5 * (K.square(delta) / K.exp(2 * sigma)))
    elif mode == 'std':
        sigma = K.clip(sigma, 1e-6, None)
        return K.mean(K.log(sigma) + 0.5 * (K.square(delta / sigma)))
    elif mode == 'mse': # mse
        return K.mean(K.square(delta - sigma), axis=-1)
    elif mode == 'mae': # mae
        return K.mean(K.abs(delta - sigma), axis=-1)
    else:
        raise ValueError


def mean_squared_logarithmic_error(y_true, y_pred, scale=1.):
    first_log = K.log(K.clip(y_pred[:, :1] * scale, K.epsilon(), None) + 1.)
    second_log = K.log(K.clip(y_true[:, :1] * scale, K.epsilon(), None) + 1.)
    return K.mean(K.square(first_log - second_log), axis=-1)


def mean_squared_signed_logarithmic_error(y_true, y_pred, scale=1.):
    first_log = K.log(K.clip(K.abs(y_pred[:, :1]) * scale, K.epsilon(), None) + 1.) * K.sign(y_pred[:, :1])
    second_log = K.log(K.clip(K.abs(y_true[:, :1]) * scale, K.epsilon(), None) + 1.) * K.sign(y_true[:, :1])
    return K.mean(K.square(first_log - second_log), axis=-1)


def rmse(y_true, y_pred):
    return K.sqrt(K.clip(mean_squared_error(y_true[:, :1], y_pred[:, :1]), K.epsilon(), None))


def smooth_L1(y_true, y_pred, clip_delta=0.5):
    x = K.abs(y_true - y_pred)[:, :1]
    x = K.switch(x < clip_delta, 0.5 * x ** 2, clip_delta * (x - 0.5 * clip_delta))
    return  K.mean(x)
