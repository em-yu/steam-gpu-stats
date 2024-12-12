import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt

df = pd.read_csv("data/steam-gpu-month-year.csv", header=None).T
df.columns = df.iloc[0] # Set column names
df.drop(0,inplace=True)
df.fillna(value=0, inplace=True)

# Convert types
df["Date"] = pd.to_datetime(df["Date"])


column_names = df.columns[1:]
for gpu_col in column_names:
    df[gpu_col] = df[gpu_col].astype('float')

print(df.head())

# Filter out months where we have no values
sum_per_month = df.sum(axis=1)
df = df[sum_per_month > 0]

mean_per_year_df = df.groupby([df["Date"].dt.year])[column_names].mean()

sum_per_year = mean_per_year_df.sum(axis=1)

usage_per_gpu_per_year = mean_per_year_df.T

# usage_per_gpu_per_year.to_csv("data/steam-gpu-users-per-year.csv", sep=";", float_format='%.3f')


# Visualization

# # Filter
# mean_per_year_df = mean_per_year_df[mean_per_year_df.columns.difference(['Other'])]
# mean_per_year_df = mean_per_year_df[mean_per_year_df.columns[(mean_per_year_df.max(axis=0) > 2).values]]


# mean_per_year_df.plot(colormap="tab20")

# plt.ylabel("percent of Steam users")

# plt.show()
