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

### shape

### image

### text

### sound

### audio


## Stimuli match expression



Stimuli match expression is a logical expression that is used to connect stimuli
definitions with the condition in which they should be presented. It is
evaluated for each condition. If the expression value is true for the current
condition than the stimuli are presented to the user in the order defined.

Currently, `and`, `or` and `=` operators can be used. There are plans for some
arithmetic and comparison operators to be added in future versions.

For example:

    parity=odd and position=left: image('red_square.png', position position) 




