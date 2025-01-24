import pandas as pd
import numpy as np
import os
from dash import *
from dateutil.relativedelta import relativedelta
import dash_mantine_components as dmc

def load_df():
    file_path = "C:\\Users\\Moritus Peters\\Documents\\plastic_chemical\\samples.tsv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The specified file '{file_path}' was not found.")
    
    df = pd.read_csv(file_path, sep="\t")
    
    """columns_to_drop = [
        "DEHP_ng_serving", "DBP_ng_serving", "BBP_ng_serving", 
        "DINP_ng_serving", "DIDP_ng_serving", "DEP_ng_serving", 
        "DMP_ng_serving", "DIBP_ng_serving", "DNHP_ng_serving", 
        "DCHP_ng_serving", "DNOP_ng_serving", "BPA_ng_serving", 
        "BPS_ng_serving", "BPF_ng_serving", "DEHT_ng_serving", 
        "DEHA_ng_serving", "DINCH_ng_serving", "DIDA_ng_serving"
    ]"""
    #df = df.drop(columns=columns_to_drop, axis=1, errors='ignore')
    
    date_columns = ["expiration_date", "manufacturing_date", "collected_on", "shipped_on"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Time difference calculations with null checks
    df['time_to_collect'] = (df["collected_on"] - df["manufacturing_date"]).dt.days
    df['time_to_ship'] = (df["shipped_on"] - df["collected_on"]).dt.days
    df['time_to_manufacture_to_ship'] = (df["shipped_on"] - df["manufacturing_date"]).dt.days
    df['time_to_manufacture_to_collect'] = (df["collected_on"] - df["manufacturing_date"]).dt.days
    
    if "manufacturing_date" in df.columns:
        df['month'] = df["manufacturing_date"].dt.to_period('M').astype(str)
    
    df['months_to_expiration'] = df.apply(
        lambda row: (relativedelta(row['expiration_date'], row['manufacturing_date']).years * 12) +
                    relativedelta(row['expiration_date'], row['manufacturing_date']).months
        if pd.notnull(row['expiration_date']) and pd.notnull(row['manufacturing_date']) else np.nan,
        axis=1
    )

    return df


# Load the dataset
df = load_df()

product_dropdown_time = dmc.Select(
    id='time_dropdown',
    label='Select product for insight',
    data=[{'label': product, 'value': product} for product in df['product'].dropna().unique()],
    value=[],
    clearable=True,
    style={'marginBottom': '20px'}
)
product_dropdown_Compostion = dmc.Select(
    id='comp_dropdown',
    label='Select product for insight',
    data=[{'label': product, 'value': product} for product in df['product'].dropna().unique()],
    value=[],
    clearable=True,
    style={'marginBottom': '20px'}
)
product_dropdown_risk = dmc.Select(
    id='risk_dropdown',
    label='Select product for insight',
    data=[{'label': product, 'value': product} for product in df['product'].dropna().unique()],
    value=[],
    clearable=True,
    style={'marginBottom': '20px'}
)


def proces_values(val):

    try:
        if isinstance(val, str):
            if '<' in val:
                num = float(val.replace('<', '').strip())
                return max(0, num - np.random.randint(1, 4))
            elif '>' in val:
                num = float(val.replace('>', '').strip())
                return num + np.random.randint(1, 4)
        return float(val)
    except ValueError:
        return np.nan

def process_chemical_values(df, chemicals):
    for chemical in chemicals:
        if chemical in df.columns:
            df[chemical] = df[chemical].apply(proces_values)

    return df




time_analysis = dcc.Markdown(
    "Time Insight exploration play an important role in determination of food contaminant how diferent time correlate witht eh collection, arrival at the lab. time, expirration date, manufacturing date and the date shipped "
)