def fcn(*args):
    out = 0
    for i in args:
        out = out + i * i
    return out


o = fcn(1, 2, 3)
print(o)

try:
    o = fcn(x=1)
except TypeError:
    print("TE")
