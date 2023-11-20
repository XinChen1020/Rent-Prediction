import pandas as pd
import sklearn
from darts import TimeSeries
from darts.models import ExponentialSmoothing

if __name__ == "__main__":
    df = pd.read_csv('Zip_zori_uc_sfrcondomfr_sm_month.csv')
    df = df.loc[df['RegionName'] == 27591]

    # Filling null values
    df = df.drop(['RegionID','SizeRank','RegionName','RegionType','StateName','State','City','Metro','CountyName'], axis=1).astype(float)
    df = df.interpolate(method='linear', axis=1, limit_direction='backward')
    df = df.melt(id_vars=[],var_name = 'Date', value_name = 'Index')
    print(df[-24:-12].mean(numeric_only=True))
    print(df[-12:].mean(numeric_only=True))
