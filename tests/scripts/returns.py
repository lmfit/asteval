def foo():
    return 1
    return 2


print(foo())

if 1:
    def bar():
        return 1
        return 2

    print(bar())


# Note: Can't do top-level returns, this is tested in test_suite.py
