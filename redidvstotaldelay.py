import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV files
df1 = pd.read_csv('delay_logs_basic.csv')
df2 = pd.read_csv('delay_logs_greedy.csv')
df3 = pd.read_csv('delay_logs_priority.csv')

# Group the data by Veh_ID and calculate the total delay for each file
grouped_df1 = df1.groupby('Veh_ID')['Total delay'].sum().reset_index()
grouped_df2 = df2.groupby('Veh_ID')['Total delay'].sum().reset_index()
grouped_df3 = df3.groupby('Veh_ID')['Total delay'].sum().reset_index()

# Plot the graph
plt.plot(grouped_df1['Veh_ID'], grouped_df1['Total delay'], color='blue', label='File 1')
plt.plot(grouped_df2['Veh_ID'], grouped_df2['Total delay'], color='green', label='File 2')
plt.plot(grouped_df3['Veh_ID'], grouped_df3['Total delay'], color='red', label='File 3')

plt.xlabel('Veh_ID')
plt.ylabel('Total Delay')
plt.title('Total Delay vs Veh_ID')
plt.legend()
plt.grid(True)
plt.show()