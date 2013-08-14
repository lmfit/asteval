SET PATH=C:\Python26;%PATH%
python setup.py bdist_wininst --target-version=2.6

SET PATH=C:\Python27;%PATH%
python setup.py bdist_wininst --target-version=2.7

SET PATH=C:\Python32;%PATH%
python setup.py bdist_wininst --target-version=3.2


