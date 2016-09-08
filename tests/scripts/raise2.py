print("Start")
try:
    try:
        1 / 0
    except:
        print("Except1")
        raise
except:
    print("Except2")

print("End")
