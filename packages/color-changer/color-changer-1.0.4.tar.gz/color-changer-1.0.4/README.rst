Python Color Changer
====================

|Build Status|

Description
-----------

This lightweight color-changer allows you to change the colors of a
given picture and creates a new file of it.

version 1.0.4

Installation
------------

You can install it from source or using ``pip``

.. code:: bash

    $ pip install color-changer

Make sure you have OpenCV installed and named cv2 as usual.
`Here <https://medium.com/coding-experiences/setting-up-opencv3-with-python3-on-macos-84be7909e28d>`__
you can find an article on how to set it up on OSX with Python3. The
other dependencies are installed automatically.

Available Arguments
-------------------

+---------+-------------+--------------------------------------+
| Short   | Long        | Values                               |
+=========+=============+======================================+
| -i      | --image     | path to image                        |
+---------+-------------+--------------------------------------+
| -c      | --changer   | red-green or gree-blue or blue-red   |
+---------+-------------+--------------------------------------+
| -r      | --result    | new image name                       |
+---------+-------------+--------------------------------------+

Examples
--------

.. code:: bash

    $ python -m colorchanger.colorchanger -i image.jpg
    $ python -m colorchanger.colorchanger -i image.png -c red-green

.. |Build Status| image:: https://travis-ci.org/DahlitzFlorian/python-color-changer.svg?branch=master
   :target: https://travis-ci.org/DahlitzFlorian/python-color-changer
