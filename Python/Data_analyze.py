import pandas as pd
import os
import matplotlib.pyplot as plt
import logging


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - %(levelname)s - "
        "[%(name)s:%(filename)s:%(lineno)d] - %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
)


plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def get_pandas():
    if os.path.exists("data"): 
        df=pd.read_csv("data/Games.csv")
        return df
    else:
        return None

def Data_cleaning(df:pd):
    isnull_df=df.isna().sum()
    if isnull_df.any():
        logging.info("存在缺失值")
    
    df['discount']=df['discount'].str.replace("%",'')
    df["discount"] = df["discount"].str.strip()
    df['discount']=pd.to_numeric(df['discount'],errors="coerce")
    negative_discount_mask =(df['discount']< -100) | (df['discount']>0)
    negative_discount=df.loc[negative_discount_mask]
    if len(negative_discount)!=0:
        logging.info("折扣百分比存在异常")

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
        logging.info("价格存在异常")
    logging.info(df)
    
    df.to_csv("data/Games.csv",encoding='utf-8',index=False)
