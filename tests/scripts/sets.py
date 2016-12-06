x = set()
print(x)

x.add("a")
print(x)
x.add("b")

y = {"a", "c"}
print(y)

print(x ^ y)
print(x | y)
print(x - y)
print(y - x)
