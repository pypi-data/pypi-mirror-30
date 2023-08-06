===============================
How to Build to RPM Packages
===============================

#. Make sure you have rpm-build installed::

    $ sudo yum install rpm-build

#. Build RPM package::

    $ sudo python setup.py bdist_rpm

#. Check if the RPM package has built::

    $ ls -1 dist/slogging*
    dist/slogging-1.0.1.devXXX-1.noarch.rpm
    dist/slogging-1.0.1.devXXX-1.src.rpm
    dist/slogging-1.0.1.devXXX.tar.gz
