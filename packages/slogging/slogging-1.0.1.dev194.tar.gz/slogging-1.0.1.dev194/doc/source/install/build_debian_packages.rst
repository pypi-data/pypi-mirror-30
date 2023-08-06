===============================
How to Build to Debian Packages
===============================

#. Make sure you have python-stdeb installed::

    sudo apt-get install python-stdeb

#. Also make sure pbr is installed as python package::

    pip install pbr

#. then::

    python setup.py --command-packages=stdeb.command bdist_deb

