# Stimuli

---

Each test description must specify a `stimuli` section.

For example:

    stimuli{
      all: shape(rectangle, position position, color color)
      error: sound(1000)
      correct: sound(500)
      fixation: shape(cross)
    }


`stimuli` section contains a list of stimuli definition statements.
Each statement is given in the form:

      <condition match expr.>: <stimuli definition>

Where `condition match expr.` is either an expression that will match one or
more conditions from the condition section or a special expression that will
match some specific event during the experiment execution.


Stimuli defined after colon in stimuli definition statement are given in the
form of list of stimulus definition. Stimuli are presented to the user in the
order they are defined.

## Stimuli types

At the moment pyFlies recognizes following stimulus types:

- **shape** - displays a shape defined in first parameter with the given color
  and location,
- **image** - displays an image from file
- **text** - displays given text at a specific location,
- **sound** - produces a tone of the given frequency and duration,
- **audio** - plays given audio file

Each stimuli type has at least one mandatory parameter and may have additional
optional parameters.  Optional parameters always start with the keyword which
identifies them, thus their order may be arbitrary. In the previous example, for
`all` condition a shape stimuli will be presented. Shape type is `rectangle`,
its position will be the value of `position` condition variable for the current
condition and its color will be the value of `color` condition variable for the
current condition.

Common stimuli parameters are:

- **duration** - is the duration in ms for which the stimuli will be presented. It
  can be a single number or the interval in the form `[ from, to ]`. If interval
  is given a random number of ms from the interval will be chosen.
- **target** - if the stimulus is marked as a target than the time should be
  measured from the presentation of this stimulus. If not given the time is
  measured from the last stimulus presented in the trial.

All visual types of stimuli has `keep` parameter which if given means that the
stimulus is not cleared when the new stimulus in the current trial is presented
(in case when there are more stimuli to show).

### shape

First parameter is mandatory and represent the shape kind. It can be
`rectangle`, `circle`, `line` or `cross`.

Additional parameters are:

- **radius** - for `circle` shape type.
- **from, to** - for `line` shape type. Coordinates are given in the form `[x,y]`.
- **size** - for `rectangle` and `cross` shape types. Size is given as an integer
  or as two integers (width, height).
- **color** - the color of the shape.
- **fillColor** - the interior color of the shape.
- **lineWidth** - the width of the shape outline.

Sizes and positions are specified in the [pyFlies coordinate
space](coordinate_system.md).  Color is currently one of predefined values:
white, black, red, yellow, green, blue, grey.


### image

This stimuli type is used to present image from file. The mandatory parameter
is a path to the file relative to the pyFlies model (see [Eriksen Flanker
example](https://github.com/igordejanovic/pyFlies/blob/master/examples/EriksenFlanker/EriksenFlanker.pf#L16).
All common parameters can be used. In addition `size` parameter can be used as
well.


### text

This stimuli type is used to present text to the user. The mandatory parameter
is the string to be presented. In addition to all common visual parameters
`size` and `color` can be given also (see [Parity
example](https://github.com/igordejanovic/pyFlies/blob/master/examples/Parity/Parity.pf#L25)).


### sound

This stimuli type is used to generate sound of the given frequency and duration.
Mandatory parameter is a frequency in Hz. Additionally, a duration in ms and
`target` param can be given.

This stimuli is used most often with `error` and `correct` match expressions
(see below).


### audio

This stimuli type is used to play sound from the file. Mandatory parameter is
audio file path relative to the pyFlies model.
In addition `duration` and `target` parameters can be given.


## Stimuli match expression

Stimuli match expression is a logical expression that is used to connect stimuli
definitions with the condition in which they should be presented. It is
evaluated for each condition. If the expression value is true for the current
condition than the stimuli are presented to the user in the order defined.

Currently, `and`, `or` and `=` operators can be used. There are plans for some
arithmetic and comparison operators to be added in future versions.

For example:

    parity=odd and position=left: image('red_square.png', position position) 


### Special match expression

There are several special match expression:

- **all** - this will match every condition thus the stimuli defined here will be
  presented for each condition from the condition table.
- **fixation** - this condition is satisfied at the beginning of the trial before
  first stimuli is presented.
- **error** - this condition is satisfied when the user response doesn't match the
  response specified in the current condition or if the time specified by the
  `duration` parameter in the `stimuli` section has lapsed.
- **correct** - this condition is satisfied if the user response match the response
  defined for the current condition.


