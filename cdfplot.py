# import pandas as pd
# import matplotlib.pyplot as plt

# # Read the CSV file into a pandas DataFrame
# file_path = 'delay_logs_priority.csv'  # Replace 'your_file.csv' with the actual path to your CSV file
# df = pd.read_csv(file_path)

# # Extract the 'Total delay' column from the DataFrame
# total_delay_column = df['Total delay']

# # Sort the 'Total delay' values in ascending order
# total_delay_sorted = total_delay_column.sort_values()

# # Calculate the cumulative probability for each data point
# cdf = total_delay_sorted.index / len(total_delay_sorted)

# # Plot the CDF
# plt.plot(total_delay_sorted, cdf, label='CDF')
# plt.xlabel('Total Delay')
# plt.ylabel('Cumulative Probability')
# plt.title('CDF for Total Delay')
# plt.legend()
# plt.grid(True)
# plt.show()
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a pandas DataFrame, considering only the first 500 rows
file_path = 'delay_logs_priority_cache_2.csv'  # Replace 'your_file.csv' with the actual path to your CSV file
df = pd.read_csv(file_path, nrows=500)

# Extract the 'Total delay' column from the DataFrame
total_delay_column = df['Total delay']

# Sort the 'Total delay' values in ascending order
total_delay_sorted = total_delay_column.sort_values()

# Calculate the cumulative probability for each data point
cdf = total_delay_sorted.index / len(total_delay_sorted)

# Plot the CDF
plt.plot(total_delay_sorted, cdf, label='CDF')
plt.xlabel('Total Delay')
plt.ylabel('Cumulative Probability')
plt.title('CDF for Total Delay (First 500 Rows)')
plt.legend()
plt.grid(True)
plt.show()
