x = range(10)
l = [1, 2, 3, 4, 5]
l[0] = 0
l[3] = -1
print(l)
l[0:2] = [-1, -2]
print(l)
l[::2] = [0, 0, 0]
print(x[1])
l[0:1] = [0, 0]
print(x[0])

