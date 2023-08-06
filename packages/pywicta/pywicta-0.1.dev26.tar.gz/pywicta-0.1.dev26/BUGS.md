# Known bugs

1. Following README.rst instructions to reinstall the library may cause the following issues:
   - "pip install --upgrade pywicta" will also upgrade external libraries like numpy, scipy, ... It's not desirable.
   - "pip install --upgrade pywicta --no-deps" does nothing...
   - So what command users should use to upgrade the library without touching external libraries ?
   - There may be issues with pip cache too during upgrade (users may have to use --no-cache-dir to force pip to check the latest version of the library on PyPI)
2. The following error happen in Travis CI (caused by the use of "from . import benchmark" in "pywi/__init__.py"):

    $ pip install pywicta
    Collecting pywicta
    Downloading pywicta-0.1.dev21.tar.gz (188kB)
    100% |████████████████████████████████| 194kB 3.6MB/s 
    Complete output from command python setup.py egg_info:
    Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "/tmp/pip-build-osxmata7/pywicta/setup.py", line 47, in <module>
    from pywicta import get_version
    File "/tmp/pip-build-osxmata7/pywicta/pywicta/__init__.py", line 46, in <module>
    from . import benchmark
    File "/tmp/pip-build-osxmata7/pywicta/pywicta/benchmark/__init__.py", line 6, in <module>
    from . import assess
    File "/tmp/pip-build-osxmata7/pywicta/pywicta/benchmark/assess.py", line 38, in <module>
    import astropy.units as u
    ModuleNotFoundError: No module named 'astropy'

