import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt

# start_date = dt(2008, 1, 1)
# end_date = dt(2024, 12, 1)

df_steam = pd.read_csv("data/steam-gpu-users-per-year.csv", sep=";")

df_perf = pd.read_csv("data/gpu-relative-performance.csv", sep=';')
df_all = pd.read_csv("data/all-gpus.csv", sep=';')
df_all["Full Name"] = df_all["Vendor"] + " " + df_all['Product Name']

df_blender = pd.read_csv("data/blender-benchmark.csv")

print(df_blender.head)

# Create a table that is handy to answer the question: what portion of the population uses a GPU that is as or more powerful than the GPU found in that paper, at this year?
# Table:
# GPU name (format: [Vendor] [Product Name]) | Relative Performance TPU (%, NaN if no value) | Benchmark median score Blender (NaN if no value)


# For every row of df_perf, find a matching row in df_steam
device_names_perf = df_perf["Device Name"]
device_names_steam = df_steam["GPU"]

tpu_perf_per_device = {}
blender_perf_per_device = {}

for idx, device_name_steam in enumerate(device_names_steam):
    # Find matching values in benchmark tables

    # Tech power up (TPU)
    matches_in_tpu = df_all[df_all["Full Name"].isin([device_name_steam])]

    if len(matches_in_tpu) > 0:
        # Get short name without Vendor to match in tpu benchmark
        product_name = matches_in_tpu.iloc[0]["Product Name"]
        
        perf_tpu_matches = df_perf[df_perf["Device Name"].isin([product_name])]
        if len(perf_tpu_matches) > 0:
            perf_tpu = perf_tpu_matches.iloc[0]["Relative Performance"]
            tpu_perf_per_device[device_name_steam] = float(perf_tpu.strip('%'))

    # Blender
    matches_in_blender = df_blender[df_blender["Device Name"].isin([device_name_steam])]
    
    if len(matches_in_blender) > 0:
        perf_blender = matches_in_blender.iloc[0]["Median Score"]
        blender_perf_per_device[device_name_steam] = perf_blender


# print(rel_perf_per_device)

df_steam["Performance (TPU)"] = df_steam["GPU"].map(tpu_perf_per_device)
df_steam["Performance (Blender)"] = df_steam["GPU"].map(blender_perf_per_device)

print(df_steam)

df_steam.to_csv("data/steam-gpus-x-benchmarks.csv", sep=";", float_format='%.3f', index=False)