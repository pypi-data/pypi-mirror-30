# NotImportChecker
Python module used on editors to check if a imported module is installed.

# Examples
## Test file
### test1.py
```python
import os

print(os.listdir('.'))

```
### test2.py
```python
import os
import dontExist

print(os.listdir('.'))

```

Use

```python
>>> from notimportchecker import *
>>> c = Checker('test1.py')
>>> c
<notimportchecker.Checker object at 0x7f172352bdd0>
>>> c.get_imports()
{'os': {'lineno': 1, 'mod_name': {'os': 'os'}}}
>>> l = c.get_not_imports_on_file(c.get_imports())
>>> c._import_error_listfLyMd-mAkEr
{}
>>> print_report(l)
There are not not imports

```
```python
>>> c = Checker('test2.py')
>>> c.get_imports()
{'os': {'lineno': 1, 'mod_name': {'os': 'os'}}, 'dontExist': {'lineno': 2, 'mod_name': {'dontExist': 'dontExist'}}}
>>> print(c.get_not_imports_on_file(c.get_imports()))
{'dontExist': {'lineno': 2, 'mod_name': 'dontExist'}}
>>> print_report(l)
dontExist module have 2 Not Imports
dontExist on line: 2

```