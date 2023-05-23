# import csv
# import matplotlib.pyplot as plt

# def read_csv_file(file_name):
#     data = []
#     with open(file_name, 'r') as file:
#         csv_reader = csv.reader(file)
#         header = next(csv_reader)  # Read the header row
#         for row in csv_reader:
#             data.append(row)
#     return data

# # def plot_total_delay(data):
# #     veh_id_delay = {}
# #     for row in data:
# #         veh_id = int(row[1])
# #         delay = float(row[7])
# #         if veh_id in veh_id_delay:
# #             veh_id_delay[veh_id].append(delay)
# #         else:
# #             veh_id_delay[veh_id] = [delay]

# #     plt.figure(figsize=(8, 6))

# #     for veh_id, delays in veh_id_delay.items():
# #         plt.plot([veh_id] * len(delays), delays, marker='o', linestyle='', markersize=10, alpha=0.5, mec='black', mew=1)

# #     # Customize the plot
# #     plt.xlabel('Veh_ID', fontsize=12)
# #     plt.ylabel('Total Delay', fontsize=12)
# #     plt.title('Total Delay per Veh_ID', fontsize=14)
# #     plt.grid(axis='both', linestyle='--', alpha=0.5)
# #     plt.xticks(fontsize=10)
# #     plt.yticks(fontsize=10)

# #     plt.show()

# # # Read the CSV file
# # data = read_csv_file('delay_logs.csv')

# # # Plot the graph
# # plot_total_delay(data)

# # import csv
# # import matplotlib.pyplot as plt
# def plot_total_delay(data):
#     veh_id_delay = {}
#     for row in data:
#         veh_id = int(row[1])
#         delay = float(row[7])
#         if veh_id in veh_id_delay:
#             veh_id_delay[veh_id].append(delay)
#         else:
#             veh_id_delay[veh_id] = [delay]

#     plt.figure(figsize=(8, 6))

#     for veh_id, delays in veh_id_delay.items():
#         # Get the x-values for the points
#         x_values = [veh_id] * len(delays)
#         # Get the y-values for the points
#         y_values = delays

#         # Plot the points with numbers
#         for x, y, distance in zip(x_values, y_values, range(1, len(x_values) + 1)):
#             plt.plot(x, y, marker='o', linestyle='', markersize=10, alpha=0.5, mec='black', mew=1)
#             plt.text(x, y, str(distance), horizontalalignment='center', verticalalignment='bottom', fontsize=8)

#     # Customize the plot
#     plt.xlabel('Veh_ID', fontsize=12)
#     plt.ylabel('Total Delay', fontsize=12)
#     plt.title('Total Delay per Veh_ID', fontsize=14)
#     plt.grid(axis='both', linestyle='--', alpha=0.5)
#     plt.xticks(fontsize=10)
#     plt.yticks(fontsize=10)

#     plt.show()

# # Read the CSV file
# data = read_csv_file('delay_logs.csv')

# # Plot the graph
# plot_total_delay(data)
import csv
import matplotlib.pyplot as plt

def read_csv_file(file_name):
    data = []
    with open(file_name, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Read the header row
        for row in csv_reader:
            data.append(row)
    return data

def plot_total_delay(data):
    veh_id_delay = {}
    for row in data:
        veh_id = int(row[1])
        delay = float(row[7])
        if veh_id in veh_id_delay:
            veh_id_delay[veh_id].append(delay)
        else:
            veh_id_delay[veh_id] = [delay]

    plt.figure(figsize=(8, 6))

    for veh_id, delays in veh_id_delay.items():
        # Get the x-values for the points
        x_values = [veh_id] * len(delays)
        # Get the y-values for the points
        y_values = delays

        # Plot the points with numbers
        for x, y, distance in zip(x_values, y_values, range(1, len(x_values) + 1)):
            plt.plot(x, y, marker='o', linestyle='', markersize=10, alpha=0.5, mec='black', mew=1)
            plt.text(x + 0.55, y, str(distance), horizontalalignment='left', verticalalignment='center', fontsize=8)

    # Customize the plot
    plt.xlabel('Veh_ID', fontsize=12)
    plt.ylabel('Total Delay', fontsize=12)
    plt.title('Total Delay per Veh_ID', fontsize=14)
    plt.grid(axis='both', linestyle='--', alpha=0.5)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    plt.show()

# Read the CSV file
data = read_csv_file('delay_logs.csv')

# Plot the graph
plot_total_delay(data)


