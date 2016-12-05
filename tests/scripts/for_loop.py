n = 0
for i in range(10):
    n += i
print(n)

n = 0
for i in range(10):
    n += i
else:
    n = -1
print(n)

for i in range(10):
    pass
else:
    print("for else")

for i in range(10):
    if i == 0:
        print("break")
        break

for i in range(10):
    if i % 2:
        print("continue")
        continue
    print("no continue")
