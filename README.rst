pyFlies
=======

pyFlies is a domain-specific language (DSL) for cognitive experiments modeling.
It is meant to be simple to learn and readable.

A code for various run-time platforms can be generated from the experiment description.
Futhermore, model can be directly interpreted if the run-time supports pyFlies.


Dependencies
------------

* Python - https://www.python.org/
* textX - https://github.com/igordejanovic/textX
* pyQt4 - http://www.riverbankcomputing.co.uk/software/pyqt/intro
* Qt 4.8 - http://www.qt.io/developers/
* dot (Graphviz) - http://www.graphviz.org/ - dot must be on your PATH for model visualization
* jinja2 - http://jinja.pocoo.org/ - for code generation


Installation
------------

First, be sure that all dependencies are in place.
If you are installing from pypi with pip, jinja2 and textX will be
automatically installed.

To install from pypi run::

  pip install pyFlies

To install from source clone git repository or download and unpack source from https://github.com/igordejanovic/pyFlies/archive/master.zip

Run setup.

::

    python setup.py install

After installation run pyFlies GUI with::

    pyflies


Screenshots
-----------
pyFlies GUI with experiment model and experiment structure visualization.

|pyFliesGUI|

Code structure visualization

|pyFliesGUICodeCentric|

.. |pyFliesGUI| image:: https://raw.githubusercontent.com/igordejanovic/pyFlies/master/docs/images/pyFliesGUI.png
.. |pyFliesGUICodeCentric| image:: https://raw.githubusercontent.com/igordejanovic/pyFlies/master/docs/images/pyFliesGUICodeCentric.png



