import pandas as pd
import numpy as np

def create_params(datas):

    df=pd.DataFrame(datas)
    names=df.columns.values
    n=names.shape[0]

    #datasに含まれる各カラムの変化率を算出する
    for i, name in enumerate(names):
        df[i]=round(df[name].pct_change(1)*100,2)

    mean=df.iloc[1:,n:].describe().loc['mean'].values
    std=df.iloc[1:,n:].describe().loc['std'].values
    cov=df.iloc[1:,n:].cov().values

    result=[mean,std,cov]

    return result


