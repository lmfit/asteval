try:
    try:
        raise ValueError("test")
    except IndexError as e:
        print("Caught:", str(e))
    except (ValueError, IOError) as e:
        print("Caught3:", str(e))

    print("Continue")

except KeyError as e:
    print("Caught2:", str(e))

print("End")
