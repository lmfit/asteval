x = [0, 1, 2]
print(x)
z = "foo"
prev, this, next = None, None, None
try:
    for y in range(len(x)):
        try:
            if y == 0:
                raise IndexError("Test msg")
            prev = x[y - 1]
        except (IndexError, TypeError) as e:
            prev = None
            print(str(e))
        except RuntimeError as e:
            print(e)
            w = "bar"

        try:
            this = x[y]
        except (IndexError, TypeError):
            this = None
            break

        try:
            next = x[y + 1]
        except (IndexError, TypeError):
            next = None

        print(prev, this, next)

except ValueError as e:
    print(e)
