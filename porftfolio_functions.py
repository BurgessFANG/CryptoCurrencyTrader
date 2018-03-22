import numpy as np
import keras.backend as K


def trim_input_arrays_to_same_length(data_object_list):

    """Trim input arrays"""

    len_min = 1E10
    for data_object in data_object_list:

        temp_len = len(data_object.close)

        if len_min > temp_len:
            len_min = temp_len

    for idx in range(len(data_object_list)):
        data_object_list[idx].close = data_object_list[idx].close[-len_min:]
        data_object_list[idx].open = data_object_list[idx].open[-len_min:]
        data_object_list[idx].high = data_object_list[idx].high[-len_min:]
        data_object_list[idx].low = data_object_list[idx].low[-len_min:]

    return data_object_list


def build_price_arrays(data_object_list, time_lag=50):

    """ Build array of currency prices """

    data_object_list = trim_input_arrays_to_same_length(data_object_list)

    price_array_training\
        = np.ones((len(data_object_list[0].close) - time_lag, len(data_object_list), time_lag, 3))

    for idx, data_object in enumerate(data_object_list):

        for time in range(time_lag):

            price_array_training[:, idx, time, 0] = data_object.close[time:-(time_lag - time)]\
                                                    / data_object.open[time:-(time_lag - time)]
            price_array_training[:, idx, time, 1] = data_object.low[time:-(time_lag - time)]\
                                                    / data_object.open[time:-(time_lag - time)]
            price_array_training[:, idx, time, 2] = data_object.high[time:-(time_lag - time)]\
                                                    / data_object.open[time:-(time_lag - time)]

    array_shape = price_array_training.shape

    price_array_training = np.concatenate(
        (price_array_training, np.ones((array_shape[0], 1, array_shape[2], array_shape[3]))), 1)

    price_array = price_array_training[:, :, 0, 0]

    return price_array, price_array_training


def calculate_portfolio_value_backend(
        portfolio_array,
        input_tensor,
        transaction_fee=0.0025):

    """ Calculate the value of a portfolio for given prices and portfolio vectors """

    # Assumes currencies can only be traded into dollars and back out.

    price_array = input_tensor[:, :, 0, 0]

    portfolio_change = portfolio_array[1:, :] - portfolio_array[:-1, :]

    shrinking_factor = 1 - K.abs(portfolio_change) * transaction_fee

    shrinking_factor = K.concatenate((K.ones((1, K.shape(shrinking_factor)[1])), shrinking_factor), axis=0)

    portfolio_value_temp = portfolio_array * shrinking_factor * price_array

    portfolio_value = K.cumprod(K.sum(portfolio_value_temp, axis=1))

    cum_log_return = K.sum(K.log(K.sum(portfolio_value_temp, axis=1)))

    return portfolio_value, cum_log_return


def calculate_portfolio_value(
        portfolio_array,
        price_array,
        transaction_fee=0.0025):

    """ Calculate the value of a portfolio for given prices and portfolio vectors """

    portfolio_change = portfolio_array[1:, :] - portfolio_array[:-1, :]

    shrinking_factor = 1 - np.abs(portfolio_change) * transaction_fee

    shrinking_factor = np.concatenate((np.ones((1, shrinking_factor.shape[1])), shrinking_factor), axis=0)

    portfolio_value_temp = portfolio_array * shrinking_factor * price_array

    portfolio_value = np.cumprod(np.sum(portfolio_value_temp, axis=1))

    cum_log_return = np.sum(np.log(np.sum(portfolio_value_temp, axis=1)))

    return portfolio_value, cum_log_return
