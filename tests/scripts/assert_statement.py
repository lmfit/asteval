n = 6
assert n == 6
print(n)

try:
    assert n == 7
except AssertionError:
    print("AE")

