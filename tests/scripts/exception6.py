try:
    try:
        raise KeyError("test")
    except IndexError as e:
        print("Caught:", str(e))
    except (ValueError, IOError) as e:
        print("Caught3:", str(e))

    print("Continue")

except KeyError as f:
    print("Caught2:", str(f))
finally:
    print("Finally2")

print("End")
