import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime as dt



df = pd.read_csv("data/steam-gpus-x-benchmarks.csv", sep=";")


# Get a list per year with values like:
# { gpu: [device-name], users_ratio: [% of users that use this gpu]}
# with the list sorted according to the selected benchmark (TPU or Blender)
def get_sorted_usage_list(
        year_start=2008,
        year_end=2024,
        benchmark="Blender"
    ):

    sorted_df = df.sort_values(f"Performance ({benchmark})", ascending=True, na_position='first')

    # remove values with NaN performance
    # devices_no_perf = sorted_df[sorted_df[f"Performance ({benchmark})"].isna()]

    device_list_per_year = []
    for year in sorted_df.columns[1:-2]:
        if int(year) < year_start:
            continue
        if int(year) > year_end:
            continue
        # remove empty values (0% users)
        empty_values_filter = sorted_df[f"{year}"] > 0
        filtered_df = sorted_df[empty_values_filter]
        # devices_usage = devices_usage[empty_values_filter]
        # devices_name = devices_name[empty_values_filter]

        # Aggregate the usage stats of GPUs with no performance benchmark, as well as those in the "Other" category
        # These correspond to GPUs we have no info about
        mystery_gpus_filter = np.logical_or(
            filtered_df[f"Performance ({benchmark})"].isna(),
            filtered_df["GPU"].isin(["Other"])
        )

        mystery_gpu_sum_usage = filtered_df[mystery_gpus_filter][f"{year}"].sum()

        print(f"Year {year}, GPUs with no known perf data: {mystery_gpu_sum_usage}")

        filtered_df = filtered_df[~mystery_gpus_filter]


        devices_name = filtered_df["GPU"]
        devices_usage = filtered_df[f"{year}"]

        device_list = [{'gpu': name, 'users_ratio': usage} for name, usage in zip(devices_name, devices_usage)]
        device_list.insert(0, {'gpu': 'Unknown', 'users_ratio': mystery_gpu_sum_usage})

        device_list_per_year.append({
            'year': year,
            'devices': device_list
        })

    return device_list_per_year


def get_overall_gpu_sorted_list(benchmark="Blender"):
    sorted_df = df.sort_values(f"Performance ({benchmark})", ascending=True, na_position='first')

    return list(sorted_df["GPU"])

def plot_sorted_gpu_usage(
        ax,
        year_start=2008,
        year_end=2024,
        benchmark="Blender",
        users_ratio_threshold=2,
        gpu_line=None
    ):

    perf_col_name = f"Performance ({benchmark})"


    # Select columns corresponding to the years we want
    years = np.arange(year_start, year_end + 1).astype(str).tolist()

    columns = ["GPU", perf_col_name] + years

    filtered_df = df[columns]

    # remove empty values (0% users)
    empty_values_filter = np.any(filtered_df[years] > 0, axis=1)
    filtered_df = filtered_df[empty_values_filter]

    # Aggregate the usage stats of GPUs with no performance benchmark, as well as those in the "Other" category
    # These correspond to GPUs we have no info about
    mystery_gpus_filter = np.logical_or(
        filtered_df[perf_col_name].isna(),
        filtered_df["GPU"].isin(["Other"])
    )

    # Compute the aggregate of users corresponding to that
    aggregate_users_mystery_gpus = filtered_df[mystery_gpus_filter][years].sum(axis=0)

    # Remove these lines
    filtered_df = filtered_df[~mystery_gpus_filter]

    # Add a line for the mystery GPUs
    # Define columns to add with an array of values for the new row(s)    
    data = {
        "GPU": ["Unknown"], 
        perf_col_name:   [0], 
    }

    for year in years:
        data[year] = [aggregate_users_mystery_gpus[year]]
        
    # We need a new DataFrame with the new contents
    df_new_rows = pd.DataFrame(data)

    # Call Pandas.concat to create a new DataFrame from several existing ones
    filtered_df = pd.concat([filtered_df, df_new_rows])

    filtered_df = filtered_df.sort_values(perf_col_name, ascending=True, na_position='first')

    # Remove the GPU names for rows where the GPU never reaches x% of users (to simplify the legend and colors)
    unpopular_gpus = np.all(filtered_df[years] < users_ratio_threshold, axis=1)

    filtered_df.loc[unpopular_gpus, "GPU"] = "ignore"

    # Transpose to have the year as index
    df_per_year = filtered_df.set_index("GPU")[years].T

    # Nb of unique (non ignored) GPUs:
    unique_gpus = list(dict.fromkeys(df_per_year.columns))

    # return filtered_df
    cmap = matplotlib.cm.get_cmap('plasma')
    colors_dict = {'ignore': 'white'}
    for idx, gpu_name in enumerate(unique_gpus):
        if gpu_name == 'ignore':
            continue
        colors_dict[gpu_name] = cmap(idx / len(unique_gpus))

    df_per_year.plot.bar(stacked=True, color=colors_dict, ax=ax)



    # Plot a line for the given GPU name
    if gpu_line is not None:
        # Get corresponding column if it exists
        gpu_col_idx = df_per_year.columns.get_loc(gpu_line)

        worse_or_eq_gpus = df_per_year.iloc[:, :gpu_col_idx+1]

        total_ratio_eq_gpus = worse_or_eq_gpus.sum(axis=1)


        print(gpu_col_idx)
        print(df_per_year.iloc[:, :gpu_col_idx])
        print(total_ratio_eq_gpus)

        total_ratio_eq_gpus.plot(ax=ax, lw=4, color='red', label=f"Cutoff for {gpu_line}")

    # Legend
    h, l = ax.get_legend_handles_labels()
    unique_h = []
    unique_l = []
    set_labels = set()
    set_labels.add("ignore") # ignore this label
    for handle, label in zip(h, l):
        if label in set_labels:
            continue
        else:
            unique_h.append(handle)
            unique_l.append(label)
            set_labels.add(label)

    unique_h.reverse()
    unique_l.reverse()

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    ax.set_title("Usage ratio for GPUs, sorted by performance")
    ax.set_xlabel("Year")
    ax.set_ylabel("Ratio of users")
    ax.legend(unique_h, unique_l, loc='center left', bbox_to_anchor=(1, 0.5))

    # plt.show()




# print(df.head) 
fig, ax = plt.subplots()

plot_sorted_gpu_usage(ax, year_start=2020, benchmark="Blender", users_ratio_threshold=2, gpu_line="NVIDIA GeForce GTX 1080")


plt.show()
