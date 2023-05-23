import csv

# Create a new CSV file with headers
def create_csv_file(file_path, headers):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
    print(f"CSV file '{file_path}' created with headers: {headers}")

# Add a new row to the CSV file
def add_row_to_csv(file_path, row_data):
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row_data)
    print(f"Row added to CSV file '{file_path}': {row_data}")

# Example usage

# Create a new CSV file
csv_file = 'test.csv'
headers = ['Req_ID', 'Veh_ID', 'Tx1','P1','Pr1','Tx2','P2','Total delay']
create_csv_file(csv_file, headers)

# Add rows to the CSV file
add_row_to_csv(csv_file, ['Jane', '30', 'Female'])
add_row_to_csv(csv_file, ['John', '25', 'Male'])
add_row_to_csv(csv_file, ['Jane', '30', 'Female'])
