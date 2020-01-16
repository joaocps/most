import numpy as np

l = np.load("converted.npy")

for item in l:
    print([item[0],item[1]])