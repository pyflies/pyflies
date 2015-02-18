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

Screen definitions are instructions which are presented to the subject
in between trial series.

4. Define the structure of the experiment::

  structure {
    screen Practice
    test Simon 1 practice randomize
    screen Real
    test Simon 10 randomize
  }

The structure gives the order and structure of execution. In its most basic
form, shown here, it instantiates screens and tests in the right order. In this
experiment, first a Practice screen will be displayed. After the user press
ENTER key a test execution will be performed for 1 set of trials (a set consists
of application of all possible conditions). In this example, there is 4 possible
conditions thus this serie will have 4 trials. This trial serie will be of
practice type which means that it should be removed from the results. A set of
conditions will be randomized.

At this point an experiment is fully described but to be usable we have to
generate the code for the target platform.

5. Configure target generator::

  target Expyriment {
    output = "/home/igor/tmp/Simon/"
    responses {
      // see expyriment/misc/constants.py
      left = K_LEFT
      right = K_RIGHT
    }

This specification defines that `Expyriment` target library is used. The output
folder where code should be generated is set. `responses` section maps abstract
responses keywords (from the `conditions` section) to the platform specific
responses (e.g. keys, buttons).

Multiple target configuration can be specified.

6. From the GUI choose `Generate code` action. The generator will produce code
   for you experiment and the configured target platform.


