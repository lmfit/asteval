print([i * i for i in range(4)])
x = [i * i for i in range(6) if i > 1]
print(x)

y = "before"
z = [y for y in range(10)]
# 'y' should be 'before' (it shouldn't leak out)
print(y)
print(z)

z = [y for y in range(10) if y > 2]
print(z)

