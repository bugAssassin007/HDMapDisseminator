import random
import time

def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    left_half = merge_sort(left_half)
    right_half = merge_sort(right_half)

    return merge(left_half, right_half)

def merge(left, right):
    result = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])

    return result

# Generate a list of 200 random numbers
numbers = [random.randint(1, 1000) for _ in range(200)]

# Measure the time taken to run the merge sort algorithm
start_time = time.time()
sorted_numbers = merge_sort(numbers)
end_time = time.time()

# Calculate the time taken in milliseconds
execution_time = (end_time - start_time) * 1000

print("Sorted numbers:", sorted_numbers)
print("Execution time:", execution_time, "milliseconds")

