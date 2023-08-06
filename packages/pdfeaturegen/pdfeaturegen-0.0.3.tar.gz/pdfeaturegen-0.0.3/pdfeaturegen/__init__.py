import pandas as pd

def generate_timestamp_features(timestamp_series):
    """
    Returns a Pandas DataFrame with new features generated from a given timestamp series

    :param timestamp_series: A pandas.Series with the timestamps
    :rtype pandas.DataFrame:
    """
    df = pd.DataFrame()
    df['time_year'] = timestamp_series.dt.year.astype('int16')
    df['time_month'] = timestamp_series.dt.month.astype('int16')
    df['time_day'] = timestamp_series.dt.day.astype('int16')
    df['time_hour'] = timestamp_series.dt.hour.astype('int16')
    df['time_minute'] = timestamp_series.dt.minute.astype('int16')
    df['time_second'] = timestamp_series.dt.second.astype('int16')
    df['time_week'] = timestamp_series.dt.week.astype('int16')
    df['time_weekday_name'] = timestamp_series.dt.weekday_name.astype('category')
    df['time_weekofyear'] = timestamp_series.dt.weekofyear.astype('int16')
    df['time_quarter'] = timestamp_series.dt.quarter.astype('int8')
    df['time_is_leap_year'] = timestamp_series.dt.is_leap_year
    df['time_is_month_end'] = timestamp_series.dt.is_month_end
    df['time_is_month_start'] = timestamp_series.dt.is_month_start
    df['time_is_quarter_end'] = timestamp_series.dt.is_quarter_end
    df['time_is_quarter_start'] = timestamp_series.dt.is_quarter_start
    df['time_is_year_end'] = timestamp_series.dt.is_year_end
    df['time_is_year_start'] = timestamp_series.dt.is_year_start
    return df

def timestamp_feature_engineering_with_df(df, timestamp_series):
    """
    Returns a new Pandas DataFrame concatenated with the new features generated from the given timestamp series

    :param df: A pandas.DataFrame with the features
    :param timestamp_series: A pandas.Series with the timestamps
    :rtype pandas.DataFrame:
    """
    timestamp_features_df = generate_timestamp_features(df.time)
    df = pd.concat([df, timestamp_features_df], axis=1)
    return df
