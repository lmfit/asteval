i = 'before'
x = {i: chr(65 + i) for i in range(4)}
print(x)
# 'i' should be 'before (shouldn't leak out of dictcomp)
print(i)


def invert(d):
    return {v: k for k, v in d.items()}


d = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
print(invert(d))


z = {i: chr(65 + i) for i in range(20) if i % 2 == 0}
print(z)
