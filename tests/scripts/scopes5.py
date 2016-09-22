x = 1
print(x)

def f():
    y = 2
    def g():
        z = 3
        print(x)
        print(y)
        print(z)
    g()

f()
print(x)

