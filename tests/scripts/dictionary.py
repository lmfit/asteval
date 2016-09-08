a_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
print(a_dict['a'] == 1)
print(a_dict['d'] == 4)

for k in a_dict.keys():
    print(k)

for v in a_dict.values():
    print(v)

for k, v in a_dict.items():
    print(k, v)

