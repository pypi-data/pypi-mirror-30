# import numpy as np
# import topopy
# from topopy.tests.testFunctions import gerber,  generate_test_grid_2d

# X = generate_test_grid_2d(40)
# Y = gerber(X)
# ct = topopy.ContourTree(debug=True)
# ct.build(X,  Y)
# print(len(ct.superNodes))

###############################################################################
import pandas as pd
from topopy import MorseSmaleComplex

df = pd.DataFrame(pd.read_csv('combustion.csv'))
print(df.columns[0:10])
print(df.columns[10])
X = df[df.columns[0:10]].as_matrix()
Y = df[df.columns[10]].as_matrix().flatten()

msc = MorseSmaleComplex(graph='relaxed beta skeleton',  max_neighbors=100,
                        normalization='feature',  aggregator='mean',
                        connect=True, debug=True)

msc.build(X,  Y)

###############################################################################

# import pandas as pd
# from topopy import MorseSmaleComplex

# df = pd.DataFrame(pd.read_csv('ackley_2D_cvt.csv'))
# X = df[df.columns[0:1]].as_matrix()
# Y = df[df.columns[2]].as_matrix().flatten()

# df = pd.read_csv('simulations.csv')
# X = df[df.columns[0:9]].as_matrix()
# Y = df[df.columns[10]].as_matrix().flatten()

# msc = MorseSmaleComplex(graph='beta skeleton',  max_neighbors=500,
#                         normalization='zscore',  aggregator='mean',  debug=True)

# msc.build(X,  Y)

# print(msc.hierarchy)
# print(msc.min_hierarchy)
# print(msc.max_hierarchy)
# # for key,  items in msc.base_partitions.items():
# #     print(key,  len(items))

# print('descending')
# for key,  items in msc.descending_partitions.items():
#     print(key,  len(items))

# print('ascending')
# for key,  items in msc.ascending_partitions.items():
#     print(key,  len(items))

###############################################################################

# import numpy as np
# import topopy

# X = np.ones((11, 2))
# X[10] = [0, 0]

# def printResults(X, Y, foo):
#     x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, foo)
#     print('')

#     for a, b in zip(x, y):
#         print(a, b)
#     print('')


# Y = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 100])
# printResults(X, Y)
# x,y = topopy.TopologicalObject.aggregate_duplicates(X,  Y)
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, 'min')
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, 'max')
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, lambda x: x[0])
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, lambda x: x[-1])
# printResults(x, y)

# printResults(X, Y)
# x, y = topopy.ContourTree.aggregate_duplicates(X,  Y)
# printResults(x, y)
# x, y = topopy.MorseSmaleComplex.aggregate_duplicates(X, Y)
# printResults(x, y)

# Y = np.array([[0, 9],
#               [1, 8],
#               [2, 7],
#               [3, 6],
#               [4, 5],
#               [5, 4],
#               [6, 3],
#               [7, 2],
#               [8, 1],
#               [9, 0],
#               [100, 0]])


# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, 'min')
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, 'max')
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, 'mean')
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, 'median')
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, 'first')
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, 'last')
# printResults(x, y)
# x, y = topopy.TopologicalObject.aggregate_duplicates(X,  Y, lambda x: x[0])
# printResults(x, y)
