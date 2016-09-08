def fcn(square=False, x=0, y=0, z=0, t=0):
    out = 0
    for i in (x, y, z, t):
        if square:
            out = out + i * i
        else:
            out = out + i
    return out


print(fcn(x=1, y=2, z=3, square=False))
print(fcn(x=1, y=2, z=3, square=True))
print(fcn(x=1, y=2, z=3, t=-2))
try:
    fcn(x=1, y=2, z=3, t=-12, s=1)
except TypeError:
    print("TE")


def fcn2(square=False, **kws):
    out = 0
    for i in kws.values():
        if square:
            out = out + i * i
        else:
            out = out + i
    return out


print(fcn2(x=1, y=2, z=3, square=False))
print(fcn2(x=1, y=2, z=3, square=True))

try:
    fcn2(1, 2, 3)
except TypeError as e:
    print("TE2")


def fcn3(x, y):
    return x + y ** 2


print(fcn3(2, 1))
print(fcn3(x=2, y=1))
print(fcn3(y=2, x=1))
try:
    print(fcn3(1, x=1))
except TypeError:
    print("TE3")
