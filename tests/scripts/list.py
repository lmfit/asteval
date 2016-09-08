a_list = ['z', 'a', 'b', 'c', 'd', 'o']
print(a_list[1] == 'a')
print(a_list[1] == 'b')
print(a_list[2] == 'c')

for x in a_list:
    print(x)

print(a_list[-1])

a_list.sort()
print(a_list)

a_list.append('z')
print(a_list)

a_list[0] = 'aa'
print(a_list)

a_list[0:1] = [1, 2]
print(a_list)

del a_list[0]
print(a_list)

a_list.extend([1, 2, 3])
print(a_list)

a_list.insert(0, 'aaa')
print(a_list)

a_list.pop(0)
print(a_list)

a_list.remove(1)
print(a_list)

a_list.reverse()
print(a_list)
