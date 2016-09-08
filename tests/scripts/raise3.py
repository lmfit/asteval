try:
    raise NameError('Foo')
except NameError:
    print("NE")
