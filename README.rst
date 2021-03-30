====================================================
BW2QSD: Bridging Brightway2 and QSD packages for LCA
====================================================

.. image:: https://img.shields.io/pypi/l/exposan?color=blue&logo=UIUC&style=flat
   :target: https://github.com/QSD-Group/BW2QSD/blob/master/LICENSE.txt
.. image:: https://img.shields.io/pypi/pyversions/bw2qsd?style=flat
   :target: https://pypi.python.org/pypi/bw2qsd
.. image:: https://img.shields.io/pypi/v/bw2qsd?style=flat&color=blue
   :target: https://pypi.org/project/bw2qsd/


What is ``BW2QSD``?
-------------------
``BW2QSD`` is an interface package to tailor the functions in `Brightway2 <https://brightway.dev/>`_ to existing and future quantitative sustainable design (QSD) packages.


Installation
------------
``BW2QSD`` requires `eidl (EcoInventDownLoader) <https://github.com/haasad/EcoInventDownLoader>`_, which is not available on PyPI. You need to firstly install ``eidl`` through conda. Detailed explanation can be found in the `tutorial <https://github.com/QSD-Group/BW2QSD/blob/main/bw2qsd/Tutorial.ipynb>`_, but TL;DR:

.. code:: bash

    conda install -c defaults -c conda-forge -c cmutel -c haasad eidl


The package can be downloaded from `PyPI <https://pypi.org/project/bw2qsd/>`_.

If you use pip:

.. code:: bash

    pip install bw2qsd


To get the git version (use the depth flag to choose how many commit histories you want to clone):

.. code:: bash

    git clone https://github.com/QSD-Group/BW2QSD.git --depth=1


Tutorial
--------
Please refer to the `tutorial <https://github.com/QSD-Group/BW2QSD/blob/main/bw2qsd/Tutorial.ipynb>`_ on GitHub for how to get started.


Author and Contributing
-----------------------
Author:

	Yalin Li: `@yalinli2 <https://github.com/yalinli2>`_; `email <zoe.yalin.li@gmail.com>`_

Please refer to the `Contributing to QSDsan <https://qsdsan.readthedocs.io/en/latest/CONTRIBUTING.html>`_ section of the documentation for instructions and guidelines.


License information
-------------------
Please refer to the ``LICENSE.txt`` for information on the terms & conditions for usage of this software, and a DISCLAIMER OF ALL WARRANTIES.