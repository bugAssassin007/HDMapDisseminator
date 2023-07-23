import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV files
df1 = pd.read_csv('delay_logs_basic.csv')
df2 = pd.read_csv('delay_logs_greedy.csv')
df3 = pd.read_csv('delay_logs_priority.csv')

# Group the data by Veh_ID and calculate the total delay for each file
grouped_df1 = df1.groupby('Veh_ID')['Total delay'].sum().reset_index()
grouped_df2 = df2.groupby('Veh_ID')['Total delay'].sum().reset_index()
grouped_df3 = df3.groupby('Veh_ID')['Total delay'].sum().reset_index()

# Plot the graph with smoother lines
x1 = grouped_df1['Veh_ID']
y1 = grouped_df1['Total delay']
x2 = grouped_df2['Veh_ID']
y2 = grouped_df2['Total delay']
x3 = grouped_df3['Veh_ID']
y3 = grouped_df3['Total delay']

plt.plot(x1, y1, color='blue', label='File 1')
plt.plot(x2, y2, color='green', label='File 2')
plt.plot(x3, y3, color='red', label='File 3')

# Interpolate the lines for smoother curves
x_smooth = np.linspace(x1.min(), x1.max(), 300)
y_smooth1 = np.interp(x_smooth, x1, y1)
y_smooth2 = np.interp(x_smooth, x2, y2)
y_smooth3 = np.interp(x_smooth, x3, y3)

plt.plot(x_smooth, y_smooth1, color='blue', linestyle='-', alpha=0.7)
plt.plot(x_smooth, y_smooth2, color='green', linestyle='-', alpha=0.7)
plt.plot(x_smooth, y_smooth3, color='red', linestyle='-', alpha=0.7)

plt.xlabel('Veh_ID')
plt.ylabel('Total Delay')
plt.title('Total Delay vs Veh_ID')
plt.legend()
plt.grid(True)
plt.show()
