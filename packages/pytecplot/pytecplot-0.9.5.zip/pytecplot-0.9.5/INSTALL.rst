Installation
============

.. highlight:: shell

..  contents::
    :local:
    :depth: 2

Python and Tecplot
------------------

.. note:: Software Requirements

    * |Tecplot 360 2017 R1| *or later*
    * |Python| *(64 bit) 2.7 or 3.4+*

    *Required Python Modules (normally installed by pip - see below):*

        * `six <https://pypi.python.org/pypi/six>`_
        * `pyzmq <https://pypi.python.org/pypi/pyzmq>`_
        * `flatbuffers <https://pypi.python.org/pypi/flatbuffers>`_
        * `future <http://python-future.org>`_ *(Python 2.7 only)*
        * `contextlib2 <http://contextlib2.readthedocs.io>`_ *(Python 2.7 only)*
        * `enum34 <https://bitbucket.org/stoneleaf/enum34>`_ *(Python 2.7 only)*

    *Optional Python Modules:*

        * `numpy <http://www.numpy.org>`_
        * `ipython <https://ipython.org>`_
        * `pillow <https://python-pillow.org>`_

.. |Tecplot 360 2017 R1| replace:: `Tecplot 360 2017 R1
    <http://www.tecplot.com/my/product-releases/tecplot-360>`__
.. |Python| replace:: `Python <https://www.python.org/downloads/>`__

|PyTecplot| is supported on 64 bit Python versions 2.7 and 3.4+. |PyTecplot|
does not support 32 bit Python. Interacting with the |Tecplot Engine| requires
a valid |Tecplot 360| installation and |Tecplot License| with |TecPLUS|
maintenance service. Visit http://www.tecplot.com for more information about
purchasing |Tecplot 360|.

For all platforms, the |Tecplot 360| application must be run once to
establish a licensing method. This will be used when running any script which
uses the python *tecplot* module.

Package Installer
^^^^^^^^^^^^^^^^^

It is recommended to use |pip| to install |PyTecplot|, along with all of the
dependencies, from Python's official `PyPI servers
<https://pypi.python.org/pypi/pytecplot>`_. The installer, |pip|, is a python
module that can be executed directly (from a console) and is part of the core
modules that come with recent version of Python. Please refer to `pip's
documentation <https://pip.pypa.io>`_ for information if you have issues using
|pip|.

Depending on the options you set when installing Python, you may already have
the folder containing |pip| in your ``PATH`` environment variable. If this is
the case, then you may use |pip| directly instead of prepending it with
``python -m`` like we show in the following commands.

If you can not get pip installed and you are running Python version 2.7, you
may be able to install it with ``easy_install`` from within a command console::

    easy_install pip

You will likely need **administrative privileges** to run the above command. If
you still do not have |pip| installed, this
`installation guide
<http://docs.python-guide.org/en/latest/starting/installation/>`_ may help.

.. _connections:

Requirements for Connecting to Tecplot 360 GUI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python scripts that use the PyTecplot package normally run in "batch" mode.
That is, PyTecplot starts it's own Tecplot Engine, thus interfacing directly
with the underlying libraries allows fast execution of a user's scripts.
PyTecplot also has the capability to connect to a running instance of Tecplot
360 through the TecUtil Server addon. Connections can be made from the local or
a remote host and the GUI will update as the script progresses, however
commands are passed through sockets and there is a high overhead cost that will
cause the script to be much slower than in batch mode.

To connect to a running Tecplot 360 instance, you must have version 2017 R3 or
later. In Tecplot 360, the TecUtil Server addon must be loaded and "listening"
on a specific port (click on "Scripting -> PyTecplot Connections...", the
default port is 7600). Then in the script, the user can call
`tecplot.session.connect()` to make the connection and the script will send all
following commands to the running Tecplot 360.

Windows
-------

.. note::

    We recommend using the latest version of Python (64 bit) with Windows since
    it comes with |pip| and will require the least amount of post-install
    configuration. The default version of Python presented to Windows users is
    32 bit which **will not work** with |PyTecplot|. You will have to navigate
    `Python's download page <https://www.python.org/downloads/windows>`_ to
    find the "x86-64" version.

Installation
^^^^^^^^^^^^

Once Python is installed along with the |pip|
module, you may install |PyTecplot| from Python's official `PyPI servers
<https://pypi.python.org/pypi/pytecplot>`_ by opening a command console and
running the following command with **administrative privileges** if needed::

    python -m pip install pytecplot

Installing from Local Source
++++++++++++++++++++++++++++

For those with a restricted internet connection, |PyTecplot| ships with
|Tecplot 360| and can be found under the ``pytecplot`` directory. You may
run pip from within this directory to install pytecplot as follows. Note that
"[VERSION]" should be replaced with the installed version of |Tecplot 360|
and the use of "." indicates the current working directory::

    cd "C:\Program Files\Tecplot\Tecplot 360 EX [VERSION]\pytecplot"
    python -m pip install .

Installing Without Administrative Privileges
++++++++++++++++++++++++++++++++++++++++++++

If you get a "permission denied" error,  this likely means you are attempting
to install |PyTecplot| into a system-controlled Python package directory. If
this is what you want to do, then you must open the command console with
**administrative privileges**. Alternatively, you may wish to install
|PyTecplot| into your user-space or home directory. This can be done by add the
option ``--user`` to the install step (see the output of the command ``python
-m pip help`` for details)::

    python -m pip install --user pytecplot

Optional Dependencies
+++++++++++++++++++++

All **required** dependencies will be installed along with |PyTecplot|. There
are optional dependencies such as `Numpy <http://www.numpy.org>`_ and `IPython
<https://ipython.org>`_ which you may want to install as well. These can be
installed by appending ``[extras]`` to the installation command::

    python -m pip install pytecplot[extras]

Environment Setup
^^^^^^^^^^^^^^^^^

Depending on the options you selected when installing |Tecplot 360|, you may
need to setup your environment so PyTecplot can find the dynamic libraries
associated with the engine. If |Tecplot 360|'s bin directory is not already
in the system's ``PATH`` list, you will have to add it and make sure it is
before any other |Tecplot 360| installation. With a standard installation of
|Tecplot 360|, the path is usually something like the following. Again,
"[VERSION]" should be replaced with the installed version of |Tecplot 360|::

    "C:\Program Files\Tecplot\Tecplot 360 EX [VERSION]\bin"

To view the current path, run the following command in the command console::

    echo %PATH%

To edit it globally for all consoles you will have to navigate to "Control
Panel" -> "System" -> "Advanced System Settings" -> "Environment Variables".
From there, you should find the ``PATH`` environment variable, edit it, and
click "OK"; no reboot is required. After changing the ``PATH``, be sure to
close and re-open your console window.

Updating
^^^^^^^^

To update |PyTecplot| after you have already installed it once, you run the
same installation command with the option ``--upgrade``. For example::

    python -m pip install --upgrade pytecplot

When installing a new version of |Tecplot 360|, you must ensure that the
``PATH`` environment variable gets updated accordingly.

Linux
-----

.. note::

    We recommend using the operating system's package manager to install and
    update Python along with |pip|. Once this is done,
    you can use ``sudo pip`` to manage the installation of system-wide python
    modules.

Installation
^^^^^^^^^^^^

Once Python is installed along with the |pip|
module, you may install |PyTecplot| from Python's official `PyPI servers
<https://pypi.python.org/pypi/pytecplot>`_ by running the following command
with **root privileges (sudo)** if needed::

    pip install pytecplot

Installing from Local Source
++++++++++++++++++++++++++++

For those with a restricted internet connection, |PyTecplot| ships with
|Tecplot 360| and can be found under the ``pytecplot`` directory. You may
run pip from within this directory to install pytecplot as follows. Note the
use of "." indicates the current working directory::

    cd /path/to/tecplot360/pytecplot
    pip install .

Installing Without Root Access
++++++++++++++++++++++++++++++

If you get a "permission denied" error,  this likely means you are attempting
to install |PyTecplot| into a system-controlled Python package directory. If
this is what you want to do, then you must prepend the above |pip| command
with **sudo**. Alternatively, you may wish to install |PyTecplot| into your
user-space or home directory. This can be done by add the option ``--user`` to
the install step (see the output of the command ``pip help`` for details)::

    pip install --user pytecplot

Optional Dependencies
+++++++++++++++++++++

All **required** dependencies will be installed along with |PyTecplot|. There
are optional dependencies such as `Numpy <http://www.numpy.org>`_ and `IPython
<https://ipython.org>`_ which you may want to install as well. These can be
installed by appending ``[extras]`` to the installation command::

    pip install pytecplot[extras]

Environment Setup
^^^^^^^^^^^^^^^^^

Once installed, you will need to setup your environment so PyTecplot can find
the dynamic libraries associated with the engine. |Tecplot 360| ships with
an environment script that, by default, outputs the appropriate shell commands
to update the appropriate environment variables. Typical usage is to pass the
output to the built-in shell command ``eval``::

    eval `/path/to/tecplot360/bin/tec360-env`

At this point |PyTecplot| should be configured for use and you may try running
the "hello world" example. If for some reason the ``tec360-env`` script fails
to work, you may add by hand the ``bin`` and ``bin/sys`` directories to the
dynamic library loader search path. This involves setting the following
environment variable (this is what the ``eval`` command above does)::

    export LD_LIBRARY_PATH=/path/to/tecplot360/bin:/path/to/tecplot360/bin/sys

You can see what this environment variable is set to by running ``echo
$LD_LIBRARY_PATH`` in the terminal.

Updating
^^^^^^^^

To update |PyTecplot| after you have already installed it once, you run the
same installation command with the option ``--upgrade``. For example::

    pip install --upgrade pytecplot

When installing a new version of |Tecplot 360|, you must ensure that the
``LD_LIBRARY_PATH`` environment variable gets updated accordingly.

Mac OSX
-------

.. note::

    We highly recommend using a package management tool such as `Macports
    <https://www.macports.org>`_, `Brew <http://brew.sh>`_ or `Fink
    <http://finkproject.org>`_ to install and update Python along with `pip
    <https://pip.pypa.io>`_. Once this is done, you can use ``sudo pip`` to
    manage the installation of system-wide python modules.

Installation
^^^^^^^^^^^^

Once Python is installed along with the |pip| module,
you may install |PyTecplot| from Python's official `PyPI servers
<https://pypi.python.org/pypi/pytecplot>`_ by running the following command
with **root privileges (sudo)** if needed::

    pip install pytecplot

Installing from Local Source
++++++++++++++++++++++++++++

For those with a restricted internet connection, |PyTecplot| ships with
|Tecplot 360| and can be found under the ``pytecplot`` directory. You may
run pip from within this directory to install pytecplot as follows. Note the
use of "." indicates the current working directory::

    cd /path/to/tecplot360/pytecplot
    pip install .


Installing Without Root Access
++++++++++++++++++++++++++++++

If you get a "permission denied" error,  this likely means you are attempting
to install |PyTecplot| into a system-controlled Python package directory. If
this is what you want to do, then you must prepend the above |pip| command
with **sudo**. Alternatively, you may wish to install |PyTecplot| into your
user-space or home directory. This can be done by add the option ``--user`` to
the install step (see the output of the command ``pip help`` for details)::

    pip install --user pytecplot

Optional Dependencies
+++++++++++++++++++++

All **required** dependencies will be installed along with |PyTecplot|. There
are optional dependencies such as `Numpy <http://www.numpy.org>`_ and `IPython
<https://ipython.org>`_ which you may want to install as well. These can be
installed by appending ``[extras]`` to the installation command::

    pip install pytecplot[extras]

Environment Setup
^^^^^^^^^^^^^^^^^

Once installed, you will need to setup your environment so PyTecplot can find
the dynamic libraries associated with the engine. |Tecplot 360| ships with
an environment script that, by default, outputs the appropriate shell commands
to update the appropriate environment variables. Typical usage is to pass the
output to the built-in shell command ``eval`` (notice the full path is wrapped
in quotes to allow for spaces)::

    eval `"/Applications/Tecplot 360 EX [VERSION]/bin/tec360-env"`

At this point |PyTecplot| should be configured for use and you may try running
the "hello world" example. If for some reason the ``tec360-env`` script fails
to work, you may add by hand the ``Contents/MacOS`` directory to the dynamic
library loader search path. This involves setting the following environment
variable (this is what the ``eval`` command above does)::

    export DYLD_LIBRARY_PATH="/Applications/Tecplot.../Contents/MacOS"

With a standard installation of |Tecplot 360|, the "Tecplot..." above is
usually something like the following. Note that "[VERSION]" should be replaced
with the installed version of |Tecplot 360|::

    "Tecplot 360 EX [VERSION]/Tecplot 360 EX [VERSION].app"

You can see what this environment variable is set to by running ``echo
$DYLD_LIBRARY_PATH`` in the terminal.

Updating
^^^^^^^^

To update |PyTecplot| after you have already installed it once, you run the
same installation command with the option ``--upgrade``. For example::

    pip install --upgrade pytecplot

When installing a new version of |Tecplot 360|, you must ensure that the
``DYLD_LIBRARY_PATH`` environment variable gets updated accordingly.

System Integrity Protection (SIP)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you installed Python (and the pip module) using `Macports
<https://www.macports.org>`_, `Brew <http://brew.sh>`_ or `Fink
<http://finkproject.org>`_, you should have little trouble using |PyTecplot|.
Please try running the "hello world" example before continuing here.

Starting with OSX version 10.11, Apple has introduced a highly restrictive
protection agent which unsets the ``DYLD_LIBRARY_PATH`` environment variable
when a sub process is created using a system-installed executable such as
``/usr/bin/python``. It is easily by-passed but requires some work on the
user's part. We present here two options: 1. Setting up a Python virtual
environment in user-space (the user's home directory) and 2. disabling Apple's
System Integrity Protection (SIP).

Using a Python Virtual Environment
++++++++++++++++++++++++++++++++++

This is the less invasive option and has several advantages as it isolates the
installation of |PyTecplot| from the system. The user has total control on
which python modules are installed and there is no need for elevated "root"
privileges. However, there is overhead involved on the user's part.
Specifically, the user is now responsible for installing all the python
packages to be used and the environment will have to "activated" before running
any scripts that require it.

Please see the `official documentation
<https://docs.python.org/3/library/venv.html>`_ concerning Python virtual
environments. If you are using Python version 2.7, please see the older
`virtualenv <https://virtualenv.pypa.io>`_ project. In short, the ``venv``
Python module is used to create a complete installation of Python in the user's
home directory::

    python -m venv myenv

This creates a directory "myenv" and installs Python into it. The virtual
environment can now be activated by sourcing the "activate" script under the
``myenv`` directory::

    source myenv/bin/activate

You should now have ``python`` and |pip| pointing to this directory::

    $ which python
    /Users/me/myenv/bin/python
    $ which pip
    /Users/me/myenv/bin/pip

From here, you should be able to install |PyTecplot| as discussed above without
root (sudo) requirements.

Disabling SIP
+++++++++++++

The system protection enforced by default on the newest versions of OSX is
controlled by the ``csrutil`` command which only allows you to change the
settings in recovery mode. To do this, you may follow these steps:

1. Restart your Mac.
2. Before OSX starts up, hold down Command-R and keep it held down until
   you see an Apple icon and a progress bar.
3. From the Utilities menu, select Terminal.
4. At the prompt, type ``csrutil disable`` and press Return.
5. Reboot.

The status of SIP can be checked by the user without being in recovery mode
with the command::

    csrutil status

You can test the propagation of the ``DYLD_LIBRARY_PATH`` environment variable
to the sub process by running the following command which will print ``True``
or ``False``::

    export DYLD_LIBRARY_PATH='test'
    /usr/bin/python -c 'import os;print("DYLD_LIBRARY_PATH" in os.environ)'

Troubleshooting
---------------

1. Verify that you have installed and can run |Tecplot 360| version **2017
   R1** *or later*.
2. Verify that you are running 64 bit Python version ``2.7`` or ``3.4+``.
3. Verify that you have run ``python -m pip install pytecplot`` with the
   correct python executable.
4. Installing into the Python's ``site-packages`` typically requires elevated
   privileges. Therefore the ``pip install`` command may need a ``sudo`` or
   "Run as Administrator" type of environment. Alternatively, you may install
   |PyTecplot| and all of its dependencies into the user's home directory with
   ``pip``'s option: ``--user``.
5. Make sure the directory pointed to by ``PATH``, ``LD_LIBRARY_PATH`` or
   ``DYLD_LIBRARY_PATH`` for Windows, Linux and OSX respectively exists and
   contains the |Tecplot 360| executable and library files.
6. Though the package is named "pytecplot" the actual python module that is
   imported is just "tecplot" - i.e. you should have "import tecplot" and not
   "import pytecplot" at the top of your scripts.
7. If your script throws an exception when you attempt to call any pytecplot
   API, the most likely cause is a missing or invalid |Tecplot License| or an
   expired |TecPLUS| maintenance service subscription. Run |Tecplot 360| and
   go to *Help* -> *Tecplot 360 EX Licensing...* to verify the license is
   configured properly.

.. note:: If the license is missing or invalid, try the following:

    1. On Windows, be sure that the latest version of |Tecplot 360| is first
       in your PATH environment variable.
    2. Check to see if you can run |Tecplot 360| by double clicking on the
       desktop icon (Windows), or from the command prompt.
    3. On Linux and Mac OSX, be sure that your LD_LIBARARY_PATH (Linux) or
       DYLD_LIBRARY_PATH is set to the latest version of |Tecplot 360|.
    4. If you are able to run |Tecplot 360| but still cannot run a script
       that imports the ``tecplot`` module, contact `Tecplot Technical Support
       <support@tecplot.com>`_.

.. highlight:: python

.. |pip| replace:: `pip <https://pip.pypa.io>`__
