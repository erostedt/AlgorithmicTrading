import numpy as np
from scipy import fft, ifft
import pandas as pd
import statsmodels.api as sm


def fourier_transform(df):
    """
    Calculates the fourier transform of some incoming data.
    :param data: Signal to be transformed.
    :return: Fourier transformed signal.
    """
    if isinstance(df, pd.Series):
        return pd.DataFrame(np.abs(fft(df)), columns=[df.name])

    fft_df = pd.DataFrame(columns=df.columns)
    for name, col in df.iteritems():
        fft_df[name] = np.abs(fft(col))
    return fft_df


def inverse_fourier_transform(df):
    """
    Calculates the inverse fourier transform of some incoming data.
    :param data: Signal to be inverse transformed.
    :return: Inversed fourier transformed signal.
    """
    if isinstance(df, pd.Series):
        return pd.DataFrame([np.abs(fft(df))], columns=[df.name])

    ifft_df = pd.DataFrame(columns=df.columns)
    for name, col in df.iteritems():
        ifft_df[name] = ifft(df)
    return ifft_df


def moving_average(df, window=10, rule='same'):
    """
    Computes a moving average of the data.
    :param data: Data to be averaged.
    :param window: Window size (Degree of the moving average).
    :param rule: ?
    :return: Moving average of prescribed data.
    """

    if isinstance(df, pd.Series):
        return pd.DataFrame(np.convolve(df, np.ones(window), rule) / window, index=df.index, columns=[df.name])

    ma_df = pd.DataFrame(columns=df.columns)
    for name, col in df.iteritems():
        ma_df[name] = np.convolve(col, np.ones(window), rule) / window

    return ma_df


def differencing(df, shift=1):
    """
    Differencing the data, i.e. (P_{i+shift} - P_{i}) for all i.
    :param data: The stock data to be transformed. Type sensitive! Must be pandas dataframe.
    :param shift: How large shift
    :return: Percentual change dataframe.
    """
    if not shift:
        shift = 1
    return df.shift(shift) - df


def pct_change(df, shift=1):
    """
    Calculates percentual change of the stock data, i.e. (P_{i+shift} - P_{i})/P_{i} for all i.
    :param data: The stock data to be transformed. Type sensitive! Must be pandas dataframe.
    :param shift: How large shift
    :return: Percentual change dataframe.
    """
    if not shift:
        shift = 1
    return df.pct_change(periods=shift)


def sarimax(df, order, seasonality=None, num_predictions=7, exog=None, trend=None, interval='D'):
    """
    Returns a df of realizations for fitted sarimax models.
    :param df: Pandas df.
    :param order: (p, d, q) -> AR = (p, 0, 0), MA = (0, 0, q), ARMA = (p, 0, q), ARIMA=(p, d, q)
    :param seasonality: Seasonality
    :param num_predictions: Add k step predictions to realization
    :param exog: Exogenous input.
    :param trend: Trend of the data, ex 'c', 't', 'ct', 'ctt'
    :param interval: How often new data comes.
    :return: df of realizations (with predictions)
    """

    t = pd.date_range(df.index[-1], periods=num_predictions + 1, freq=interval).drop(df.index[-1])
    sarimax_df = pd.DataFrame(columns=df.columns)
    preds_df = pd.DataFrame(columns=df.columns, index=t)

    if len(order) == 2:
        order = (order[0], 0, order[1])

    if isinstance(exog, pd.DataFrame):
        exog.to_numpy()

    for name, col in df.iteritems():

        model = sm.tsa.statespace.SARIMAX(col, exog, order=order, seasonal_order=seasonality, trend=trend)
        model_result = model.fit()
        realization = model_result.predict(start=df.index[0], end=df.index[-1])

        sarimax_df[name] = realization

        if num_predictions:
            for pred_idx in range(num_predictions):
                forecast = model_result.forecast(steps=num_predictions)
                preds_df[name] = forecast.values
    sarimax_df = pd.concat([sarimax_df, preds_df], axis=0)

    return sarimax_df


def varmax(df, order=(1, 0), num_predictions=7, exog=None, trend=None, interval='D'):
    """
        Returns a df of realizations for fitted varmax models.
        :param df: Pandas df.
        :param order: (p, q) -> AR = (p, 0), MA = (0, q), ARMA = (p, q)
        :param num_predictions: Add k step predictions to realization
        :param exog: Exogenous input.
        :param trend: Trend of the data, ex 'c', 't', 'ct', 'ctt'
        :param interval: How often new data comes.
        :return: df of realizations (with predictions)
        """
    t = pd.date_range(df.index[-1], periods=num_predictions + 1, freq=interval).drop(df.index[-1])
    model = sm.tsa.VARMAX(df, exog, order, trend)
    model_res = model.fit()
    varmax_df = model_res.predict(start=df.index[0], end=df.index[-1])
    preds_df = pd.DataFrame(model_res.forecast(steps=num_predictions).values, columns=df.columns, index=t)
    varmax_df = pd.concat([varmax_df, preds_df], axis=0)

    return varmax_df
