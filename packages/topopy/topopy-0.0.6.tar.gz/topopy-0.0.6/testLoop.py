import pandas as pd

from topopy import MorseSmaleComplex

df = pd.read_csv('deployment.csv')
X = df[df.columns[0:6]].as_matrix()
Y = df[df.columns[7]].as_matrix().flatten()
print(df.columns[0:6])
print(df.columns[7])

# df = pd.read_csv('combustion_cleaned.csv')
# X = df[df.columns[0:9]].as_matrix()
# Y = df[df.columns[10]].as_matrix().flatten()

msc = MorseSmaleComplex(graph='relaxed beta skeleton', max_neighbors=500,
                        normalization='feature', debug=True)

msc.build(X, Y)
