import numpy as np

def sort_centroids(centroids):
    # Sort centroids by y-coordinate
    sorted_by_y = sorted(centroids, key=lambda k: k[1])

    # Sort each batch of three centroids by x-coordinate
    sorted_batches = [sorted(sorted_by_y[i:i + 3], key=lambda k: k[0]) for i in range(0, len(sorted_by_y), 3)]

    # Flatten and reshape into a 3x3x2 array
    return np.array([c for batch in sorted_batches for c in batch]).reshape(3, 3, 2)


