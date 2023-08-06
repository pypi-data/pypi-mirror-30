import pandas as pd
import pandas.util.testing as pdt

from .data import read_time_series_csv


def assert_ts_frame_equal(df, filename, generate_ref=False, precision=10):
    df = df if isinstance(df, pd.DataFrame) else df.to_frame()
    df.columns = df.columns.astype(str)
    df = df.round(precision)
    if generate_ref:
        df.to_csv(filename)
    else:
        df_ref = read_time_series_csv(filename)
        pdt.assert_frame_equal(df_ref, df, check_less_precise=precision)
