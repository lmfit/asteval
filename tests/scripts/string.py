x = 1
print(str(1))
x = "xxxx"
print(str(x))
x = True
print(str(x))
x = 1.0
print(str(x))
x = {"a": 1}
print(str(x))
x = [1, 2, 3]
print(str(x))

print("xxx".capitalize())
print("ß".casefold())
print("xxx".center(20))
print("xxxyyyzzz".count('xx'))
print("xxxß".encode("utf-8"))
print("xxx/".endswith('/'))
print('01\t012\t0123\t01234'.expandtabs(4))
print('Py' in 'Python')
print("The sum of 1 + 2 is {0}".format(1+2))
try:
    "xxx".index("yyy")
except ValueError:
    print("VE")

print("XXX".lower())
print('   spacious   '.lstrip())
print('www.example.com'.lstrip('cmowz.'))
