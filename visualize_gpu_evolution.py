import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt

start_date = dt(2023, 1, 1)
end_date = dt(2023, 12, 1)

with open('steam_gpu_per_year.csv', newline='') as file:
    csv_data = list(csv.reader(file))
    labels = csv_data[0]

    # xs = np.arange(len(labels) - 1) # first col of a row is GPU name and not a y value
    for row_idx in range(1, len(csv_data)):
        line_label = csv_data[row_idx][0]
        if line_label == 'Other':
            continue
        gpu_x = []
        gpu_y = []
        for col_idx in range(1, len(csv_data[row_idx])):
            
            # Filter date?
            date = dt.strptime(labels[col_idx], '%Y-%m')
            if date.timestamp() > end_date.timestamp() or date.timestamp() < start_date.timestamp():
                continue

            x = col_idx - 1
            y = csv_data[row_idx][col_idx]
            if y != '':
                y = float(y)
                gpu_x.append(x)
                gpu_y.append(y)

        # only plot if there are some significantly large values for this GPU
        if len(gpu_x) > 0 and max(gpu_y) > 2:
            plt.plot(gpu_x, gpu_y, label=line_label)

# Filter labels
labels_in_range = []
x_ticks = []
for x_idx, date_label in enumerate(labels[1:]):
    date = dt.strptime(date_label, '%Y-%m')
    if date.timestamp() <= end_date.timestamp() and date.timestamp() >= start_date.timestamp():
        labels_in_range.append(date_label)
        x_ticks.append(x_idx)


plt.xticks(x_ticks, labels_in_range)
plt.legend(bbox_to_anchor=(1.05, 1), fontsize='small')
plt.show()