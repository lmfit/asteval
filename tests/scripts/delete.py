# Del dict keys
x = {'a': 1, 'b': 2}
print('a' in x)
print(len(x))
del x['a']
print('a' in x)
print(len(x))

# Del names
y = 'a'
print(y)
del y
try:
    print(y)
except NameError:
    print("NE")

# Del list items
z = [1, 2, 3]
del z[-1]
print(z)

# Del list w/stride
a = [1, 2, 3, 4, 5, 6]
del a[::2]
print(a)
