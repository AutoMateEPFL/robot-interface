import numpy as np

number = 7
x_id = number//4
y_id = number if number in [0, 1, 2, 3] else number-4
print(y_id)

a = [1, 2, 3, 4]
for item in reversed(a) :
    print(item)