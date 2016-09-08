print(abs(-1))
print(all([1, 2, 3]))
print(any([1, 2, 3]))
print(bin(123))
print(bool("x"))
print(bytearray("xxx", "ascii"))
print(bytes("xxx", "ascii"))
print(complex(1, 2))
print(divmod(10, 6))
for i, x in enumerate([1, 2, 3]):
    print(i, x)

def more_than(x, m=3):
    return x > m

for x in filter(more_than, [1, 2, 3, 4, 5]):
    print(x)

print(float("3.14"))
print(float("-Infinity"))
print(hash("xxx"))
print(hex(123))
print(int("123"))
print(int("123deadbeef", base=16))
x = 1
print(isinstance(x, int))
print(len("xxx"))

def double(x):
    return x*2

for x in map(double, [1, 2, 3, 4]):
    print(x)

print(max(2, 3, 4))
print(min(1, 2, 3))
print(oct(123))
print(ord("x"))
print(pow(1, 2, 3))
print(list(range(7)))
for x in reversed([1, 2, 3]):
    print(x)

print(round(3.14))
print(round(2.5))
print(set())
print(sorted([3, 2, 1]))
print(sum([1, 2, 3]))
print(tuple([1, 2, 3]))
print(type(list()))
for x, y in zip([1, 2, 3], [4, 5, 6]):
    print(x, y)

