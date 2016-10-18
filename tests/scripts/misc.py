def a():
    al = ['TestA']
    return al

def b():
    bl = ['TestB']
    return bl

def c():
    cl = ['TestC']
    return cl

def d():
    dl = ['TestD']
    return dl

def e():
    el = ['TestE']
    #el.append('TestE')
    return el

def f():
    fl = ['TestF']
    return fl

def doall():
    l1 = a() + b() + c()
    l2 = d() + e() + f()
    return (l1, l2)

(l1, l2) = doall()
print(l1)
print(l2)
