poolmanager
===========

[![Build Status](https://travis-ci.org/geoadmin/lib-poolmanager.svg?branch=master)](https://travis-ci.org/geoadmin/lib-poolmanager)

## Simple pool manager implementation for unordered results

poolmanager is compatible with python 2.6, 2.7, 3.6

### Usage

`ctrl+c` will automatically terminate the main process and
thus all the associated subprocesses. You'll need to wait for all the
functions to finish their current execution before being able to stop
all the processes. One can also easily create a callback function to monitor
the computation state.


```python
from poolmanager import PoolManager

def add(x):
    return x + 1.5

def callback(counter, result):
    print 'counter: %s' % counter
    print 'result: %s' % result

def main():
    chunk = 2
    iterator = xrange(0, 10)
    pm = PoolManager(numProcs=2, factor=2, store=True)
    pm.imap_unordered(add, iterator, chunk, callback=callback)

if __name__ == '__main__':
    main()

>> counter: 1
>> result: 1.5
>> counter: 2
>> result: 2.5
>> counter: 3
>> result: 5.5
>> counter: 4
>> result: 6.5
>> counter: 5
>> result: 7.5
>> counter: 6
>> result: 8.5
>> counter: 7
>> result: 3.5
>> counter: 8
>> result: 4.5
>> counter: 9
>> result: 9.5
>> counter: 10
>> result: 10.5

print [i for i in iterator]
print pm.results

>> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>> [1.5, 2.5, 5.5, 6.5, 7.5, 8.5, 3.5, 4.5, 9.5, 10.5]

```

### Tests

```
python setup.py test
```

### Publish a new version of the module

Edit `$HOME/.pypirc` and add (username and password in keepass):

```
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
repository=https://upload.pypi.org/legacy/
username=iwi***
password=

[pypitest]
repository=https://test.pypi.org/legacy/
username=iwi***
password=
```

Bump version in `setup.py`.

Upload the new module to the test repository:

```
pip install --upgrade setuptools
python setup.py sdist upload -r pypitest
python setup.py bdist_wheel upload -r pypitest
```

Test local install from test repository.

```
pip install -i https://test.pypi.org/simple/ poolmanager
```

If everything is ok, push the new version to the default repository.

```
python setup.py sdist upload -r pypi
python setup.py bdist_wheel upload -r pypi
```

Test the newly created module.

Create a RELEASE in github.

### CONTRIBUTORS:

- [Gilber Jeiziner](https://github.com/gjn)
- [Loïc Gasser](https://github.com/loicgasser)
