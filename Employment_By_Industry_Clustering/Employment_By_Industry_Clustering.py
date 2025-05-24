import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import os

# Change directory
os.chdir('C:/Users/jerom/OneDrive/Courses/LinkedIn/Employment_By_Industry_Clustering')

# Load the employment data from CSV
# Assumes the first column is 'Industry' and the rest are numeric employment changes
df = pd.read_csv("employment_industry.csv")
df.set_index(df.columns[0], inplace=True)

# Perform hierarchical clustering
distance_matrix = pdist(df.values, metric='euclidean')
linked = linkage(distance_matrix, method='ward')

# Save and show the dendrogram
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "employment_dendrogram.png")

plt.figure(figsize=(10, 6))
dendrogram(linked, labels=df.index.tolist(), orientation='right')
plt.title('Dendrogram of Employment Changes by Industry')
plt.xlabel('Distance')
plt.tight_layout()
plt.savefig(output_path, dpi=300)
plt.show()