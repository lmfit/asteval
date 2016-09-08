def foo():
    x = 1 / 0


try:
    foo()
except:
    print("Boom!")
