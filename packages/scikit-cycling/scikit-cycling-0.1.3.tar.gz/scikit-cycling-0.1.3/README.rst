Scikit-cycling
==============

.. image:: https://travis-ci.org/scikit-cycling/scikit-cycling.svg?branch=master
    :target: https://travis-ci.org/scikit-cycling/scikit-cycling

.. image:: https://ci.appveyor.com/api/projects/status/f2mvtb9y1mcy99vg?svg=true
    :target: https://ci.appveyor.com/project/glemaitre/scikit-cycling

.. image:: https://readthedocs.org/projects/scikit-cycling/badge/?version=latest
    :target: http://scikit-cycling.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/scikit-cycling/scikit-cycling/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/scikit-cycling/scikit-cycling

.. image:: https://badges.gitter.im/Join%20Chat.svg
  :target: https://gitter.im/scikit-cycling/Lobby?utm_source=share-link&utm_medium=link&utm_cam

Installation
------------

Dependencies
~~~~~~~~~~~~

Scikit-cycling requires:

* scipy
* numpy
* pandas
* six
* fit-parse
* joblib
* scikit-learn


Installation
~~~~~~~~~~~~

``scikit-cycling`` is currently available on the PyPi’s reporitories and you can
install it via pip::

  pip install -U scikit-cycling

The package is release also in conda-forge::

  conda install -c conda-forge scikit-cycling

If you prefer, you can clone it and run the ``setup.py`` file. Use the
following commands to get a copy from Github and install all dependencies::

  git clone https://github.com/scikit-cycling/scikit-cycling.git
  cd scikit-cycling
  pip install .

Or install using ``pip`` and GitHub::

  pip install -U git+https://github.com/scikit-cycling/scikit-cycling.git
