rdate
=====

Alternative to standard datetime library.

*IMPORTANT NOTE: No timezone support!*

There is currently no timezone support. It is assumed that all dates and times are local.


Installation
------------

.. code-block:: bash

    $ pip install rlib-date

Getting Started
---------------

.. code-block:: python

    from rdate import Date, Time

    t = Time.now()
    t = Time(22)  # 10:00:00 pm

    d = Date.today()
    d = Date(2017)  # 2017-01-01


Check the doc strings and unit tests for examples.

License
-------

"MIT". See LICENSE for details. Copyright t5w5h5@gmail.com, 2018.
