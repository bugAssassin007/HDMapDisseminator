import matplotlib.pyplot as plt

hits = [356, 480, 413]  # Example list of hits
misses = [124, 0, 73]  # Example list of misses

categories = ['Basic broadcast', 'Greedy broadcast', 'Priority broadcast']  # Categories or labels for the data

# Plotting the data
plt.bar(categories, hits, label='Hits')
plt.bar(categories, misses, bottom=hits, label='Misses')

# Adding labels and titles
plt.xlabel('Categories')
plt.ylabel('Count')
plt.title('Hits and Misses')
plt.legend()

# Displaying the plot
plt.show()
