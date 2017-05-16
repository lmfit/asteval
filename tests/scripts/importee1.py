y = 1

def foo(z):
    return 42 + z + y

#print(foo(0))  # 43

# For some reason, when run on the cmdline, python3 outputs this print -
# when run from exec() in this test suite, it does not. Leaving this commented
# out for now until it gets figured out.
