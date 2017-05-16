import importee1

y = importee1.y


def bar(z):
    return importee1.foo(z)

print(bar(2))  # 45
