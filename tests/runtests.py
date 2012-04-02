import os
import sys

pref = sys.prefix + '/lib/python2.6/site-packages'
print pref
os.system('coverage run --source=asteval unittest_1.py')
os.system("coverage report")
os.system("coverage html")
