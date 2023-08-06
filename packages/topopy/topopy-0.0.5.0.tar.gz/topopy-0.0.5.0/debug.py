# import numpy as np
# import topopy
# from topopy.tests.testFunctions import gerber, generate_test_grid_2d

# X = generate_test_grid_2d(40)
# Y = gerber(X)
# ct = topopy.ContourTree(debug=True)
# ct.build(X, Y)
# print(len(ct.superNodes))

###############################################################################

import pandas as pd
from topopy import MorseSmaleComplex

df = pd.DataFrame(pd.read_csv('ackley_2D_cvt.csv'))
X = df[df.columns[0:1]].as_matrix()
Y = df[df.columns[2]].as_matrix().flatten()

# df = pd.read_csv('combustion_cleaned.csv')
# X = df[df.columns[0:9]].as_matrix()
# Y = df[df.columns[10]].as_matrix().flatten()

msc = MorseSmaleComplex(graph='beta skeleton', max_neighbors=500,
                        normalization='zscore', aggregator='mean', debug=True)

msc.build(X, Y)

print(msc.hierarchy)
print(msc.min_hierarchy)
print(msc.max_hierarchy)
# for key, items in msc.base_partitions.items():
#     print(key, len(items))

print('descending')
for key, items in msc.descending_partitions.items():
    print(key, len(items))

print('ascending')
for key, items in msc.ascending_partitions.items():
    print(key, len(items))