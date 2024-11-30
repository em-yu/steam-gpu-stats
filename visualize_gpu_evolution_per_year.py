import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt

start_date = dt(2008, 1, 1)
end_date = dt(2024, 12, 1)

df = pd.read_csv("steam_gpu_per_year.csv", header=None).T
df.columns = df.iloc[0] # Set column names
df.drop(0,inplace=True)
df.fillna(value=0, inplace=True)

# Convert types
df["Date"] = pd.to_datetime(df["Date"])


column_names = df.columns[1:]
for gpu_col in column_names:
    df[gpu_col] = df[gpu_col].astype('float')

print(df.head())

mean_per_year_df = df.groupby([df["Date"].dt.year])[column_names].mean()

# Filter
mean_per_year_df = mean_per_year_df[mean_per_year_df.columns.difference(['Other'])]
mean_per_year_df = mean_per_year_df[mean_per_year_df.columns[(mean_per_year_df.max(axis=0) > 2).values]]


mean_per_year_df.plot(colormap="tab20")

plt.ylabel("percent of Steam users")

plt.show()
