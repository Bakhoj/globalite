# Globalite
![PyPI - Version](https://img.shields.io/pypi/v/globalite)
![GitHub License](https://img.shields.io/github/license/bakhoj/globalite)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/bakhoj/globalite/unittest.yml)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/bakhoj/globalite/python-publish.yml)

A python library for easy global variables saved to a SQLite db and accessable from multiple programs at ones.


## Supported types
|Type|Read|Write|Delete|
|:-|:-|:-|:-|
|bool|✅|✅|✅|
|int|✅|✅|✅|
|float|✅|✅|✅|
|str|✅|✅|✅|
|dict|⚠️~1~|✅|⚠️~1~|
|custom classes|❌~2~|❌~2~|❌~2~|


⚠️~1~: When reading a dict you will receive a new instance of the dict and not a reference.  
meaning that the following is the case:
```python
import globalite
gl = globalite.get_default_globalite()
gl.a_dict = {"a": 1}
assertEqual(gl.a_dict, gl.a_dict) # is true
assertIs(gl.a_dict, gl.a_dict) # is false
```
