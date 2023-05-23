import pandas as pd

def swap_columns_and_add_row_numbers(file_path):
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Add row numbers as a new column at the end
    df['row_number'] = range(1, len(df) + 1)

    # Get the column names
    columns = df.columns.tolist()

    # Find the indices of the 'matrix_indices' and 'tile_name' columns
    matrix_indices_index = columns.index('matrix_indices')
    tile_name_index = columns.index('tile_name')

    # Swap the columns
    columns[matrix_indices_index], columns[tile_name_index] = columns[tile_name_index], columns[matrix_indices_index]

    # Reorder the columns
    df = df[columns]

    # Write the updated DataFrame back to the CSV file
    df.to_csv(file_path, index=False)

# Example usage
file_path = 'long_datatotest.csv'
swap_columns_and_add_row_numbers(file_path)
