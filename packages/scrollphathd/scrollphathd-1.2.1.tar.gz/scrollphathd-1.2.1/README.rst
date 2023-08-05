|Scroll pHAT HD| https://shop.pimoroni.com/products/scroll-phat-hd

17x7 pixels of single-colour, brightness-controlled, message scrolling
goodness!

Installing
----------

Full install (recommended):
~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've created an easy installation script that will install all
pre-requisites and get your Scroll pHAT HD up and running with minimal
efforts. To run it, fire up Terminal which you'll find in Menu ->
Accessories -> Terminal on your Raspberry Pi desktop, as illustrated
below:

.. figure:: http://get.pimoroni.com/resources/github-repo-terminal.png
   :alt: Finding the terminal

In the new terminal window type the command exactly as it appears below
(check for typos) and follow the on-screen instructions:

.. code:: bash

    curl https://get.pimoroni.com/scrollphathd | bash

Alternatively, on Raspbian, you can download the ``pimoroni-dashboard``
and install your product by browsing to the relevant entry:

.. code:: bash

    sudo apt-get install pimoroni

(you will find the Dashboard under 'Accessories' too, in the Pi menu -
or just run ``pimoroni-dashboard`` at the command line)

If you choose to download examples you'll find them in
``/home/pi/Pimoroni/scrollphathd/``.

Manual install:
~~~~~~~~~~~~~~~

Library install for Python 3:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

on Raspbian:

.. code:: bash

    sudo apt-get install python3-scrollphathd

other environments:

.. code:: bash

    sudo pip3 install scrollphathd

Library install for Python 2:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

on Raspbian:

.. code:: bash

    sudo apt-get install python-scrollphathd

other environments:

.. code:: bash

    sudo pip2 install scrollphathd

Development:
~~~~~~~~~~~~

If you want to contribute, or like living on the edge of your seat by
having the latest code, you should clone this repository, ``cd`` to the
library directory, and run:

.. code:: bash

    sudo python3 setup.py install

(or ``sudo python setup.py install`` whichever your primary Python
environment may be)

In all cases you will have to enable the i2c bus.

Documentation & Support
-----------------------

-  Guides and tutorials - https://learn.pimoroni.com/scroll-phat-hd
-  Function reference - http://docs.pimoroni.com/scrollphathd/
-  GPIO Pinout - https://pinout.xyz/pinout/scroll\_phat\_hd
-  Get help - http://forums.pimoroni.com/c/support

Unofficial / Third-party libraries
----------------------------------

-  Java library by Jim Darby - https://github.com/hackerjimbo/PiJava
-  Rust library by Tiziano Santoro -
   https://github.com/tiziano88/scroll-phat-hd-rs
-  Go library by Tom Mitchell -
   https://github.com/tomnz/scroll-phat-hd-go

.. |Scroll pHAT HD| image:: scroll-phat-hd-logo.png
