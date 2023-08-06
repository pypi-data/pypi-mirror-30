
# OCAD

This is a python-modul which contains usefull fuctions when handling with ocad-files.

### Install

$ pip install ocad

### Example


```python
from ocad import ocad
```


```python
ocad.file_is_cs("OCAD12-File-Sample.ocd")

    >>>False
```

```python
ocad.file_is_map("OCAD12-File-Sample.ocd")

    >>>True
```

```python
ocad.file_is_ocad("OCAD12-File-Sample.ocd")

    >>>True
```

```python
ocad.file_version("OCAD12-File-Sample.ocd", format='short')

    >>>'12'
 ```


```python
ocad.file_info("OCAD12-File-Sample.ocd")

 >>>{'epsg_code': None,
     'epsg_name': None,
     'georeferenced': True,
     'note': 'map note',
     'number_of_backgroundmaps': 0,
     'number_of_classes': 0,
     'number_of_colors': 1,
     'number_of_courses': 0,
     'number_of_spot-colors': 0,
     'scale': '10000.000000',
     'typ': 'map',
     'version_long': '12.3.1',
     'version_short': '12'}
```



