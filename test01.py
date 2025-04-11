import numpy as np

arr = np.array([1,1.5,-0.5,-4,-100,34.234,-0.0000234])

make1 = arr / np.abs(arr)


print(make1)

ones = np.full(7,1)

make1 = (make1 + ones) / 2

print(make1)