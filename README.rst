pyFlies
=======

pyFlies is a domain-specific language (DSL) for behaviour experiments modeling.
It is meant to be simple to learn and readable.

A code for various run-time platforms can be generated from the experiment description.
Futhermore, model can be directly interpreted if the run-time supports pyFlies.


Dependencies
------------

 * Python - https://www.python.org/
 * textX - https://github.com/igordejanovic/textX
 * GTK+3 with SourceView - http://www.gtk.org/
 * dot (Graphviz) - http://www.graphviz.org/ - dot must be on your PATH for model visualization
 * jinja2 - http://jinja.pocoo.org/ - for code generation


Installation
------------

Clone git repository or download and unpack archive.
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

.. |pyFliesGUI| image:: https://github.com/igordejanovic/pyFlies/tree/master/docs/images/pyFliesGUI.png
.. |pyFliesGUICodeCentric| image:: https://github.com/igordejanovic/pyFlies/tree/master/docs/images/pyFliesGUICodeCentric.png



