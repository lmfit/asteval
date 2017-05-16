import importee0

print(importee0.y)  # 1
print(importee0.bar(1))  # 44

y = 0

def bar(w):
    print(w)
    return w * w

print(bar(2))
print(y)
