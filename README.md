# python-utilz

Set of handy python utilities.

## Installation

```shell
pip install python-utilz
```

## Contents

* [Get size of an object](#get-size-of-an-object)
* [Convert exception to string](#convert-exception-to-string)
* [Check UUID corrects without casting](#check-uuid-corrects-without-casting)
* [Human-readable time](#human-readable-time)
* [Human-readable size](#human-readable-size)
* [Separate digits](#separate-digits)
* [Now](#now)
* [Config from env](#config-from-env)

### Get size of an object

Returns total size in bytes (when you do not want full-fledged library for this).

```python
import python_utilz as pu

print(pu.get_size([1, 2, 3]))
# 172
```

### Convert exception to string

Show more info than just `str(exc)`.

```python
import python_utilz as pu

print(repr(pu.exc_to_str(TimeoutError('test'))))
# 'TimeoutError: test'
```

### Check UUID is correct without casting

When you want to check UUID, but do not want try-except on `UUID(value)`.

```python
import python_utilz as pu

print(pu.is_valid_uuid('lol-kek'))
# False
```

### Human-readable time

Created to display difference between two timestamps.

```python
import python_utilz as pu

print(repr(pu.human_readable_time(9999999)))
# '16w 3d 17h 46m 39s'

print(repr(pu.htime(1742579085.0 - 1741924401.0)))
# '1w 13h 51m 24s'
```

### Human-readable size

Created to display total amount of bytes in something.

```python
import python_utilz as pu

print(repr(pu.human_readable_size(999999999)))
# '953.7 MiB'

print(repr(pu.hsize(10000000000)))
# '9.3 GiB'
```

### Separate digits

When you want number to be more readable.

```python
import python_utilz as pu

print(repr(pu.sep_digits(123456789)))
# '123 456 789'
```

### Now

Returns current datetime in UTC timezone.

```python
import python_utilz as pu

print(pu.now())
# 2025-03-21 18:13:34.954740+00:00
```
