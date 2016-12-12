# NOTE: Sorted lists added to prevent key ordering from affecting results

x = set()
print(x)

x.add("a")
print(x)
x.add("b")
print(x)

y = {"a", "c"}
print(sorted(list(y)))

print(sorted(list(x ^ y)))
print(sorted(list(x | y)))
print(sorted(list(x - y)))
print(sorted(list(y - x)))
