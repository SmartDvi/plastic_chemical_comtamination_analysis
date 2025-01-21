import pandas as pd
import os

def load_df():
    # Check if the file exists
    file_path = "C:\\Users\\Moritus Peters\\Documents\\plastic_chemical\\samples.tsv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The specified file '{file_path}' was not found.")
    
    # Read the dataset
    df = pd.read_csv(file_path, sep="\t")
    
    # Drop unnecessary columns
    columns_to_drop = [
        "DEHP_ng_serving", "DBP_ng_serving", "BBP_ng_serving", 
        "DINP_ng_serving", "DIDP_ng_serving", "DEP_ng_serving", 
        "DMP_ng_serving", "DIBP_ng_serving", "DNHP_ng_serving", 
        "DCHP_ng_serving", "DNOP_ng_serving", "BPA_ng_serving", 
        "BPS_ng_serving", "BPF_ng_serving", "DEHT_ng_serving", 
        "DEHA_ng_serving", "DINCH_ng_serving", "DIDA_ng_serving"
    ]
    df = df.drop(columns=columns_to_drop, axis=1, errors='ignore')
    
    # Convert date columns to datetime
    date_columns = ["expiration_date", "manufacturing_date", "collected_on", "shipped_on"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Calculate time differences
    df['time_to_collect'] = (df["collected_on"] - df["manufacturing_date"]).dt.days
    df['time_to_ship'] = (df["shipped_on"] - df["collected_on"]).dt.days
    df['time_to_manufacture_to_ship'] = (df["shipped_on"] - df["manufacturing_date"]).dt.days
    df['time_to_manufacture_to_collect'] = (df["collected_on"] - df["manufacturing_date"]).dt.days
    
    # Aggregate by month
    if "manufacturing_date" in df.columns:
        df['month'] = df["manufacturing_date"].dt.to_period('M').astype(str)

    return df

# Load the dataset
df = load_df()
