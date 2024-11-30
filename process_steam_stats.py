import json
from datetime import datetime as dt
import re
import csv

snapshot_file = "2024-11-29-snapshots-all.jl"

# Result: a CSV file 
# Headers: GPU_name   |    Jan 2008    |    Feb 2008    |    ....    | Oct 2024
# Values : [string]   |    [float]     |     ....
# the values correspond to the percentage of users who have that GPU at the given time
# or None if there is no data for that GPU at this point in time

# We first store data as a dictionary, to facilitate look ups
data_per_GPU = {}
# {
#    [GPU_name]: {[date]: percentage, [date]: percentage, ...}
# }

min_recorded_timestamp = dt.now().timestamp()
max_recorded_timestamp = 0

max_timestamps_count = 10
timestamps = 0

# Open the file in read mode
with open(snapshot_file, 'r') as file:
    # Read each line in the file
    for timestamp_str in file:
        # Each line is one snapshot of the webpage
        time_stamp_data = json.loads(timestamp_str)
        date = dt.fromtimestamp(time_stamp_data['timestamp'])
        date_str = date.strftime('%Y-%m-%d')
        year = date.year
        # prev_month_date = date - timedelta(days=30)
        # prev_month_str = prev_month_date.strftime('%b').lower()

        if "ALL VIDEO CARDS" in time_stamp_data['values']:
            gpu_main_table = time_stamp_data['values']["ALL VIDEO CARDS"]
        elif "All Video Cards" in time_stamp_data['values']:
            gpu_main_table = time_stamp_data['values']["All Video Cards"]
        else:
            print(f"Error: could not find the main table in snapshot at {date_str}")
            continue
        
        if len(gpu_main_table) == 0:
            print(f"Error: main table empty in snapshot at {date_str}")
            continue

        months = gpu_main_table[0]
        # format them in the standard way
        months = list(map(lambda x: x.lower().capitalize(), months))

        # print(months)

        # go through all the rows of that table (after the first, that correspond to headings)
        for row_idx in range(1, len(gpu_main_table)):
            row = gpu_main_table[row_idx]
            if len(row) == 0:
                continue
            gpu_name = row[0].strip()
            # store in the dictionary
            if gpu_name not in data_per_GPU:
                data_per_GPU[gpu_name] = {}
            for col_idx in range(1, len(row)):
                month_idx = col_idx - 1 # because the table contains the GPU name at the first column
                month_handled = dt.strptime(months[month_idx], '%b').month

                date_key = dt(year, month_handled, 1).strftime('%Y-%m')
                # print(date_key)

                if date_key not in data_per_GPU[gpu_name]:
                    txt_value = row[col_idx]
                    value_match = re.match(r"([\d\.]+)%", txt_value) 
                    if value_match is not None:
                        value = value_match.group(1)
                    else:
                        # print(txt_value)
                        value = 0

                    data_per_GPU[gpu_name][date_key] = value

                # update date records
                max_recorded_timestamp = max(dt(year, month_handled, 1).timestamp(), max_recorded_timestamp)
                min_recorded_timestamp = min(dt(year, month_handled, 1).timestamp(), min_recorded_timestamp)

        # timestamps += 1
        # if timestamps > max_timestamps_count:
        #     break

print(f"data is available between dates {dt.fromtimestamp(min_recorded_timestamp).strftime('%Y-%m')} and {dt.fromtimestamp(max_recorded_timestamp).strftime('%Y-%m')}")

min_date = dt.fromtimestamp(min_recorded_timestamp)
max_date = dt.fromtimestamp(max_recorded_timestamp)

# Flatten data into a 2D table (GPU x time)

csv_table = []

# Headers
header_row = ["GPU name"]
for year in range(min_date.year, max_date.year + 1):
    for month in range(1, 13):
        date_key = dt(year, month, 1).strftime('%Y-%m')
        header_row.append(date_key)

csv_table.append(header_row)


# Create one row per GPU name, one column per month
for gpu_name, values_per_year in data_per_GPU.items():
    row = [gpu_name]
    for year in range(min_date.year, max_date.year + 1):
        for month in range(1, 13):
            date_key = dt(year, month, 1).strftime('%Y-%m')
            if date_key in values_per_year:
                row.append(values_per_year[date_key])
            else:
                row.append(None)
    csv_table.append(row)


# print(csv_table)

with open('steam_gpu_per_year.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(csv_table)