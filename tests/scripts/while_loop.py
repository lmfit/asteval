n = 0
while n < 8:
    n += 1

print(n)

n = 0
while n < 8:
    n += 1
    if n > 3:
        break
else:
    n = -1

print(n)

n = 0
while n < 8:
    n += 1
else:
    n = -1

print(n)

n, i = 0, 0
while n < 10:
    n += 1
    if n % 2:
        continue
    i += 1

print(n, i)

n = 0
while n < 10:
    n += 1
    if n > 5:
        break

print(n)
