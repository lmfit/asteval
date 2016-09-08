print("Start")
x = 1
y = 0
out, ok, clean = 0, False, False
try:
    out = x / y
except ZeroDivisionError:
    out = -1
    print("Boom!")
else:
    ok = True
    print("Else")
finally:
    clean = True
    print("Finally")
print(out)
print(ok)
print(clean)
