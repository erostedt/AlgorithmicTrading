import pandas as pd


def mean(df, as_df=False):
    """
    Calculates mean for all columns in dataframe
    :param df: Pandas Dataframe.
    :return: columnwise means.
    """
    return pd.DataFrame(df.mean(), columns=['Mean']) if as_df else df.mean()


def var(df):
    """
    Calculates variance for all columns in dataframe
    :param df: Pandas Dataframe.
    :return: columnwise variances.
    """
    return df.var()


def std(df):
    """
    Calculates std for all columns in dataframe
    :param df: Pandas Dataframe.
    :return: columnwise stds.
    """
    return df.std()


def corr(df):
    """
    Calculate correlation matrix between categories in dataframe.
    :param df: Pandas Dataframe.
    :return: Correlation matrix.
    """
    if isinstance(df, pd.Series):
        return pd.DataFrame([1], columns=[df.name], index=[df.name])

    return df.corr()


def cov(df):
    """
    Calculate covariance matrix between categories in dataframe.
    :param df: Pandas Dataframe.
    :return: Covariance matrix.
    """
    if isinstance(df, pd.Series):
        return pd.DataFrame([df.var()], columns=[df.name], index=[df.name])

    return df.cov()
