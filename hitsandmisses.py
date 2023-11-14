import matplotlib.pyplot as plt

hits = [612, 1946]  # Example list of hits
misses = [1348, 14]  # Example list of misses

categories = ['Basic/Periodic broadcast',  'Adaptive broadcast']  # Categories or labels for the data

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
