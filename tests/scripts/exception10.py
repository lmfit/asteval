x = []
print(x)
try:
    print(x[0])
except IndexError as e:
    print("Exception!")

print("Continue")
