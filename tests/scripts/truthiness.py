def tf(x):
    if x:
        print("True")
    else:
        print("False")


tf(1)
tf(0)
tf('1')
tf('')
tf([1])
tf([])
tf((1))
tf((0,))
tf(())
tf(dict(y=1))
tf({})
