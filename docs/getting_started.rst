Getting started
###############

Prerequsites
------------

To install pyFlies you will need to install following dependencies:

 * `Python`_
 * `textX`_ - will be installed automatically if `pip` is used.
 * `GTK+3`_ with SourceView. GUI library.
 * `pyGObject`_ - python binding for GTK+
 * `dot` (part of `GraphViz`_) - `dot` must be on your PATH for model visualization.
 * `jinja2` - for generating source code. Will be installed automatically if `pip` is used.


It is planed to make installers for different platforms available in the future.
If you want to contribute installer for some platform please se section `Contributions`.


.. _Python: https://www.python.org/
.. _textX: https://github.com/igordejanovic/textX
.. _GTK+3: http://www.gtk.org/
.. _pyGObject: https://wiki.gnome.org/Projects/PyGObject
.. _GraphViz: http://www.graphviz.org/
.. _jinja2: http://jinja.pocoo.org/

Installation
------------

pyFlies can be installed using `pip` installer::

    pip install pyFlies

or from source::

    git clone https://github.com/igordejanovic/pyFlies.git
    cd pyFlies
    python setup.py install

Quick start
-----------

1. Start pyFlies GUI.

::

   pyflies

2. Open new file and write your experiment description::


    experiment "Simon"
    "
    A simple behavioural task to assess a Simon effect.

    See also:
    http://en.wikipedia.org/wiki/Simon_effect
    "

    test Simon {
      conditions {
        position  color   congruency    response

        left      green   congruent     left
        left      red     incongruent   right
        right     green   incongruent   left
        right     red     congruent     right
      }

      stimuli{
        all: shape(rectangle, position position, color color)
        error: sound(1000)
        fixation: shape(cross)
      }
    }

3. Add screen definitions:

::

  screen Practice {
    Simon test
    ----------

    You will be presented with a colored rectangle positioned
    left or right.
    Press LEFT for the GREEN rectangle and right for the red.

    Press SPACE for the practice block.
  }

  screen Real {
    Simon test
    ----------

    Now a REAL testing will be performed.

    Press SPACE for the real block.
  }

Description consists of a set of parsing rules which at the same time
describe Python classes that will be used to instantiate object of your model.

2. Create meta-model from textX language description:

.. code:: python

  from textx.metamodel import metamodel_from_file
  hello_meta = metamodel_from_file('hello.tx')

3. Optionally export meta-model to dot (visualize your language abstract syntax):

.. code:: python

  from textx.export import metamodel_export
  metamodel_export(hello_meta, 'hello_meta.dot')

|hello_meta.dot|

You can see that for each rule from language description an appropriate
Python class has been created. A BASETYPE hierarchy is built-in. Each
meta-model has it.

4. Create some content (i.e. model) in your new language (``example.hello``):

::

  hello World, Solar System, Universe

Your language syntax is also described by language rules from step 1.

5. Use meta-model to create models from textual description:

.. code:: python

  example_hello_model = hello_meta.model_from_file('example.hello')

Textual model ‘example.hello’ will be parsed and transformed to a plain
Python object graph. Object classes are those defined by the meta-model.

6. Optionally export model to dot to visualize it:

.. code:: python

  from textx.export import model_export
  model_export(example_hello_model, 'example.dot')

|example.dot|

This is an object graph automatically constructed from ‘example.hello’
file.

7. Use your model: interpret it, generate code … It is a plain Python
   graph of objects with plain attributes!

.. _Arpeggio: https://github.com/igordejanovic/Arpeggio
.. _Xtext: http://www.eclipse.org/Xtext/

.. |hello_meta.dot| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/hello_meta.dot.png
.. |example.dot| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/example.dot.png


