x = [False, False, False, False]
for y in x:
    if y:
        break

else:
    print("Else")

print("Continue")

x = [False, False, True, False]
for y in x:
    if y:
        break

else:
    print("Else2")

print("End")

n = 0
for i in range(10):
    n += i
    if n > 2:
        break
else:
    n = -1

print(n)
