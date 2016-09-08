try:
    try:
        raise IndexError("test")
    except IndexError as e:
        print("Caught:", str(e))
    except (ValueError, IOError) as e:
        print("Caught3:", str(e))
    except:
        print("Bare")
    else:
        print("Else")
    finally:
        print("Finally")

    print("Continue")

except ValueError as e:
    print("Caught2:", str(e))

print("End")
