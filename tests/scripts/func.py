try:
    sqrt(2)
except NameError:
    from math import sqrt


def fcn(x, scale=2):
    out = sqrt(x)
    if scale > 1:
        out = out * scale
    return out

a = fcn(4, scale=9)
print(a)

try:
    a = fcn()
except TypeError:
    print("TE")

try:
    a = fcn(foo=2)
except TypeError:
    print("TE2")
