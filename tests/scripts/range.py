x = range(1)
y = range(1, 2)
z = range(1, 2, 3)
try:
    e = range(1, 2, 3, 4)
except TypeError:
    print("TE")
