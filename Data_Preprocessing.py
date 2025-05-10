# https://colab.research.google.com/drive/1OBKYpViMmxnU3Lze76cPSYOv7DWLv9h_?usp=sharing
#imports
import pandas as pd
import numpy as np
import random
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

%matplotlib Inline

# Reading Dataset
data = pd.read_csv("C:\web\Fraud-detection\Database\bank_transactions_data_2.csv")
data.head()

#Visualizing data
df=data.copy()
df.info()
print("Summary Statistics:")
print(df.describe)
print("Missing Values:")
print(df.isnull().sum())
unique_acc=df['AccountID'].unique()
len(unique_acc)

#Preprocessing data
def preprocessing_data(df):
    # Ensure datetime format
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
    df['PreviousTransactionDate'] = pd.to_datetime(df['PreviousTransactionDate'])

    # Sort transactions chronologically
    df = df.sort_values(by=['AccountID', 'TransactionDate'])

    # Time delta features
    df['TimeSinceLastTransaction'] = (df['TransactionDate'] - df['PreviousTransactionDate']).dt.total_seconds() / 3600

    # Transaction hour and day
    df['TransactionHour'] = df['TransactionDate'].dt.hour
    df['TransactionDay'] = df['TransactionDate'].dt.dayofweek

    # Rolling average transaction amount (last 3 transactions)
    df['RollingMeanAmount'] = df.groupby('AccountID')['TransactionAmount'].transform(lambda x: x.rolling(window=3, min_periods=1).mean())
    df['RollingStdAmount'] = df.groupby('AccountID')['TransactionAmount'].transform(lambda x: x.rolling(window=3, min_periods=1).std().fillna(0))

    # Deviation from usual amount
    df['AmountDeviation'] = abs(df['TransactionAmount'] - df['RollingMeanAmount']) / (df['RollingStdAmount'] + 1e-6)

    # Rolling average transaction amount (last 3 transactions)
    df['RollingMeanAmount'] = df.groupby('AccountID')['TransactionAmount'].transform(lambda x: x.rolling(window=3, min_periods=1).mean())
    df['RollingStdAmount'] = df.groupby('AccountID')['TransactionAmount'].transform(lambda x: x.rolling(window=3, min_periods=1).std().fillna(0))

    # Deviation from usual amount
    df['AmountDeviation'] = abs(df['TransactionAmount'] - df['RollingMeanAmount']) / (df['RollingStdAmount'] + 1e-6)

    # 3. Encode categorical features
    # Simple encodings (you can refine with frequency encoding if needed)
    categorical_cols = ['TransactionType', 'Channel']
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # Encode occupation as one-hot (or frequency encoding if many classes)
    df = pd.get_dummies(df, columns=['CustomerOccupation'], drop_first=True)

    df['LocationChanged'] = df.groupby('AccountID')['Location'].transform(lambda x: x != x.shift()).astype(int)
    df['DeviceChanged'] = df.groupby('AccountID')['DeviceID'].transform(lambda x: x != x.shift()).astype(int)
    df['MerchantChanged'] = df.groupby('AccountID')['MerchantID'].transform(lambda x: x != x.shift()).astype(int)

    return df
    
def drop_columns(df):
    drop_cols = ['TransactionID', 'AccountID', 'TransactionDate', 'PreviousTransactionDate',
                'Location', 'DeviceID', 'IP Address', 'MerchantID' , 'RollingMeanAmount' ,'RollingStdAmount' ,]

    df_features = df.drop(columns=drop_cols)
    return df_features
