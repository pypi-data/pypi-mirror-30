BgLogs
======

|bl| is a wrapper around the logging module of Python,
which includes a few logging setting that are helpful for us.

|bl| is intended to be used in **applications** and not in libraries.
This is because on import, |bl| configures the logging module.


How to use
----------

For applications
****************

The basic usage of ``bglogs`` should be:

.. code:: python

   import bglogs

   def f():
      bglogs.info('Info msg')


The supported functions are the same as in the logging module:
``debug``, ``info``, ``warning``, ``exception``, ``error``, ``critical``
but ``log``.

What **bglogs** gives in advantage, is that the application
main logger name is inferred once and used with no need to indicate it.
Essentially, is similar to use the ``root logger``.

If you want to indicate a name for the logger, you can use
the :meth:`get_logger` method. E.g.:


.. code:: python

   def f():
      logger = bglogs.get_logger(__name__)
      logger.info('Info msg')


You can use the :meth:`get_logger` method which is an alias of the logging
library method :meth:`getLogger`. The only difference is that
if you do not provide th logger name, the inferred logger name is used.



For libraries
*************

If you are developing a library rather than an application,
you should not use |bl|.
The reason in that |bl| configures the `logging module <https://docs.python.org/3/library/logging.html>`_
and a library should not do this as explained in
https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library

In contrast, you can add the `NullHandler <https://docs.python.org/3/library/logging.handlers.html#nullhandler>`_ to the
main logger of your library as explained in http://docs.python-guide.org/en/latest/writing/logging/#logging-in-a-library
In your main ``__init__.py`` write:

.. code:: python

   import logging
   logging.getLogger(__name__).addHandler(logging.NullHandler())

And then get the logger for each module:

.. code:: python

   logger = logging.getLogger(__name__)


.. important::

   If you do not add the `NullHandler <https://docs.python.org/3/library/logging.handlers.html#nullhandler>`_,
   the logger will inherit the root logger configuration
   (which might be what you want or not).


For mixed packages
******************

If you have a package that is intended to be used as a library,
but you also provide a command line interface to be used an application
you can still use |bl|, but care must be taken.

Ideally, you should use the logging module as in any other library.
Then, put the command line interface in a separate module (which is not imported by the other modules)
and only import |bl| from that module. This way, |bl| will only be called in you use the command line interface.



Configuration
-------------

When you import |bl| the `logging module <https://docs.python.org/3/library/logging.html>`_ is configured.
This configuration makes the root logger
to collect all ``WARNING`` and more severe log messages to the standard error
and the |if| and |db| messages to the standard output.
However, the default level is ``WARNING``, so |if| and
|db| messages from the libraries will be silenced unless they are
explicitly configured for that.
The main logger of the application will be configured to pass to the root logger
all messages with a |db| level.

The format of the messages corresponds to ``%(asctime)s %(name)s %(levelname)s -- %(message)s``
and a date format ``%Y-%m-%d %H:%M:%S``.


.. note:: In the case that your application is using other packages
   that also use |bl|, make sure that you application imports
   |bl| before importing those packages.


Further configuration
*********************

|bl| allows to do some simple configuration for different loggers
by setting their level to |if| or |db|.

This is done with the ``configure`` function.
This function can receive 2 parameters.

- The *debug* parameter indicates whether to configure the logger
  to |db| or |if|. By default it is |if|.
- The *name* parameter indicates which is the name of the logger to
  configure. If is not passed, it will be inferred.


For example, to set the application logger according to a debug flag:

.. code:: python

   def main(debug_flag):
       bglogs.configure(debug=debug_flag)

To configure a library (``bgparsers``) to |if| level:

.. code:: python

   def main():
       bglogs.configure(name='bgparsers', debug=False)



License
-------

`LICENSE <LICENSE.txt>`_.


.. |bl| replace:: **bglogs**
.. |db| replace:: ``DEBUG``
.. |if| replace:: ``INFO``
