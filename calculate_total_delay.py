import csv

def calculate_total_delay_sum(file_path):
    total_delay_sum = 0

    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_delay = float(row['Total delay'])
            total_delay_sum += total_delay

    return total_delay_sum

# Example usage
file_path = 'delay_logs_priority_original.csv'
sum_of_total_delay = calculate_total_delay_sum(file_path)
print("Sum of Total delay:", sum_of_total_delay)
