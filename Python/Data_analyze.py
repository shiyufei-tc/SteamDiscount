import pandas as pd
import os

def get_pandas():
    if os.path.exists("data"): 
        df=pd.read_csv("data/Games.csv")
        return df
    else:
        return None

def Data_cleaning(df:pd):
    isnull_df=df.isna().sum()
    if isnull_df.any():
        print("存在缺失值")
    
    df['discount']=df['discount'].str.replace("%",'')
    df["discount"] = df["discount"].str.strip()
    df["discount"] = df["discount"].astype(int)
    negative_discount_mask =(df['discount']< -100) | (df['discount']>0)
    negative_discount=df.loc[negative_discount_mask]
    if len(negative_discount)!=0:
        print("折扣百分比存在异常")

    df['original_price']=df['original_price'].str.replace("NT$",'')
    df['final_price']=df['final_price'].str.replace("NT$",'')
    df["original_price"] = df["original_price"].str.strip()
    df["final_price"] = df["final_price"].str.strip()
    df["original_price"] = df["original_price"].str.replace(",", "", regex=False)
    df["final_price"] = df["final_price"].str.replace(",", "", regex=False)
    df["original_price"] = df["original_price"].astype(float)
    df["final_price"] = df["final_price"].astype(float)
    negative_o_price_mask=df['original_price']<0
    negative_f_price_mask=df['final_price']<0
    negative_o_price=df.loc[negative_o_price_mask]
    negative_f_price=df.loc[negative_f_price_mask]
    if len(negative_f_price)!=0 or len(negative_o_price)!=0:
        print("价格存在异常")
    print(df)
