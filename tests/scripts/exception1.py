print("Start")
try:
    1 / 0
except IndexError:
    print("IE")
except Exception:
    print("ZDE")
except:
    print("Bare")
else:
    print("Else")

print("End")
