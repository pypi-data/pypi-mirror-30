=================================
PyWI CTA - A CTA wrapper for PyWI
=================================

Copyright (c) 2016-2018 Jeremie DECOCK (www.jdhp.org)

* Online documentation: https://jeremiedecock.github.io/pywi-cta/
* Source code: https://github.com/jeremiedecock/pywi-cta
* Issue tracker: https://github.com/jeremiedecock/pywi-cta/issues
* PyWI on PyPI: https://pypi.org/project/pywicta/
* PyWI on Anaconda Cloud: https://anaconda.org/jdhp/pywicta

.. Former documentation: http://sap-cta-data-pipeline.readthedocs.io/en/latest/

Description
===========

PyWI-CTA is a `ctapipe <https://github.com/cta-observatory/ctapipe>`_ wrapper for `PyWI <https://github.com/jeremiedecock/pywi>`_.

Note:

    This project is in beta stage.


Dependencies
============

.. Highly inspired by http://docs.astropy.org/en/stable/_sources/install.rst.txt

PyWI has the following strict requirements:

* `Python <https://www.python.org/>`_ 3.5 or 3.6
* `Numpy <http://www.numpy.org/>`_

PyWI also depends on other packages for optional features:

* `Scipy <https://www.scipy.org/>`_
* `Scikit-image <http://scikit-image.org/>`_
* `Pillow (a.k.a. PIL) <https://pillow.readthedocs.io/en/latest/>`_ to read and write many image formats (PNG, JPEG, TIFF, ...)
* `Astropy <http://www.astropy.org/>`_ to provide Fits file format
* `Pandas <http://pandas.pydata.org/>`_
* `Matplotlib <http://matplotlib.org/>`_ 1.5 or later to provide plotting functionality
* `PyWI <https://github.com/jeremiedecock/pywi>`_
* `Cosmostat iSAP Sparce2D <http://www.cosmostat.org/software/isap/>`_

However, note that these only need to be installed if those particular features
are needed. PyWI will import even if these dependencies are not installed.

.. _install:

Installation
============

Using pip
---------

Most major projects upload official packages to the *Python Package Index*.
They can be installed on most operating systems using Python standard `pip`
package manager.

Note that you need to have `Python3.x` and `pip` already installed on your system.

.. warning::

    Users of the Anaconda python distribution should follow the instructions
    for Anaconda install (see `Using conda`_ bellow).

.. note::

    You will need a C compiler (e.g. ``gcc`` or ``clang``) to be installed to
    install some dependencies (e.g. Numpy).

.. note::

    The ``--no-deps`` flag is optional, but highly recommended if you already
    have Numpy installed, since otherwise pip will sometimes try to "help" you
    by upgrading your Numpy installation, which may not always be desired.

.. note::

    If you get a ``PermissionError`` this means that you do not have the
    required administrative access to install new packages to your Python
    installation.  In this case you may consider using the ``--user`` option
    to install the package into your home directory. You can read more
    about how to do this in the `pip documentation
    <https://pip.pypa.io/en/stable/user_guide/#user-installs>`_.

    Alternatively, if you intend to do development on other software that uses
    PyWI, such as an affiliated package, consider installing PyWI into a
    `virtualenv <http://docs.astropy.org/en/stable/development/workflow/virtualenv_detail.html#using-virtualenv>`_.

    Do **not** install PyWI or other third-party packages using ``sudo``
    unless you are fully aware of the risks.

On MacOSX and Gnu/Linux
~~~~~~~~~~~~~~~~~~~~~~~

You can install PyWI using the following command (in a terminal)::

    pip install pywicta --no-deps

.. python -m pip install --user numpy scipy matplotlib pandas

.. It is recommended to use the --user flag to ``pip`` (note: do not use sudo pip,
.. which can cause problems) to install packages in your local user space instead
.. of the shared system directories.
.. TODO: the --user flag has an issue (bug?): console scripts (pywicta-mrfilter, ...)
.. are not directly (i.e. without updating the PATH variable) available anymore (at
.. least on MacOSX/Anaconda).

As an alternative, you can install PyWI from the downloaded source code::

    python3 setup.py install --no-deps

.. There's also a package for Debian/Ubuntu::
.. 
..     sudo apt-get install pywicta

If PyWI is already installed on your system you can upgrade it with this command::

    pip install --upgrade pywicta

To uninstall PyWI, type::

    pip uninstall pywicta

On Windows
~~~~~~~~~~

.. Note:
.. 
..     The following installation procedure has been tested to work with Python
..     3.4 under Windows 7.
..     It should also work with recent Windows systems.

You can install PyWI using the following command (in a `command prompt`_)::

    py -m pip install pywicta --no-deps

.. It is recommended to use the --user flag to ``pip`` (note: do not use sudo pip,
.. which can cause problems) to install packages in your local user space instead
.. of the shared system directories.
.. TODO: the --user flag has an issue (bug?): console scripts (pywicta-mrfilter, ...)
.. are not directly (i.e. without updating the PATH variable) available anymore (at
.. least on MacOSX/Anaconda).

As an alternative, you can install PyWI from the downloaded source code::

    py setup.py install --no-deps

If PyWI is already installed on your system you can upgrade it with this command::

    py -m pip install --upgrade pywicta

To uninstall PyWI, type::

    py -m uninstall pywicta


.. _anaconda_install:

Using conda
-----------

To install this package with conda run in a terminal::

    conda install -c jdhp pywicta

So far, the PyWI Anaconda package is only available for MacOSX.
A package for Linux and Windows will be available soon.

.. note::

    Attempting to use `pip <https://pip.pypa.io>`__ to upgrade your installation of PyWI may result
    in a corrupted installation.

Cosmostat iSAP Sparce2D installation
====================================

1. Download http://www.cosmostat.org/wp-content/uploads/2014/12/ISAP_V3.1.tgz (see http://www.cosmostat.org/software/isap/)
2. Unzip this archive, go to the "sparse2d" directory and compile the sparse2d
   library. It should generate two executables named ``mr_transform`` and ``mr_filter``::

    tar -xzvf ISAP_V3.1.tgz
    cd ISAP_V3.1/cxx
    tar -xzvf sparse2d_V1.1.tgz
    cd sparse2d
    compile the content of this directory

An automated compilation and installation script for Linux is available
`there <https://github.com/tino-michael/tino_cta/blob/master/grid/compile_mrfilter_pilot.sh>`_
(author: `Tino Michael <https://github.com/tino-michael>`_).

.. Also available in `utils/compile_isap_sparce2d.sh`

Example
=======

1. Get a simtel file (e.g. from `there <https://forge.in2p3.fr/projects/cta_analysis-and-simulations/wiki/Monte_Carlo_Productions>`_)
2. In your system terminal, from the directory that contains the sample image,
   type the following commands (where `SIMTEL_FILE` is the path to your simtel
   file)::
  
    pywicta-mrtransform -f common_hard_filtering -t 13.,1.5 -L mask --camid LSTCam --max-images 1 --plot SIMTEL_FILE
    pywicta-mrfilter -K -k -C1 -m3 -n4 -s2,4.5,3.5,3 --kill-isolated-pixels --camid LSTCam --max-images 1 --plot SIMTEL_FILE

3. Type ``pywicta-mrtransform -h`` or ``pywicta-mrfilter -h`` to display the list of
   available options and their documentation.

.. A "benchmark mode" can also be used to clean images and assess cleaning
.. algorithms (it's still a bit experimental): use the additional option ``-b all``
.. in each command (and put several fits files in input e.g. ``\*.fits``)

IPython/Jupyter Notebooks
=========================

PyWI provide some Jupyter notebooks that can be used as examples or tutorials.

* PyWI Notebooks on GitHub: https://github.com/jeremiedecock/pywi-cta-notebooks
* PyWI Notebooks on Anaconda Cloud: https://anaconda.org/jdhp/notebooks

Bug reports
===========

To search for bugs or report them, please use the PyWI Bug Tracker at:

    https://github.com/jeremiedecock/pywi-cta/issues


.. _command prompt: https://en.wikipedia.org/wiki/Cmd.exe
