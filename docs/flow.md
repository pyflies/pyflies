# Experiment flow

---

Experiment flow is specified in the `flow` block given after all test/screens
specification and it consists of a series of statements for executing a test,
showing a screen or repeating a test or a statement block.

Here is an example of how experiment flow may look like:

    flow {
        show Intro for 5000
        execute Parity(practice true, random true)

        show Real
        // repeat test 2 times, each repetition will be randomized
        repeat 2 times Parity(random true)
    }
    

## Showing screens

In the above example, we see that first the `Intro` screen is shown to the
subject for 5s. `for` definition is optional and if not given screen will be
displayed until the subject provide some input (keypress, mouse click etc.).

We can [pass arguments to screen](#passing-arguments-to-tests-and-screens) which
can be used to introduce variable parts in the screen content. For details see
the [screens section](screens.md).


## Executing tests

Each test definition may be executed many times during the course of the test.
Test is executed with `execute` statement after which we give the name of the
test and optionally argument values. `execute` is just an alias of 

    repeat 1 time <test name>

See the [looping section](#looping) for details on the `repeat` statement.


## Passing arguments to tests and screens

As you may have notice in the above example, we may pass arguments to screens
and tests. These arguments will be available as variables in the context of the
test/screen.

For example:

        execute Parity(practice true, random true, some_param 42)

Argument can have any name and any value type. Two arguments of `bool` type have
special meaning: `practice` and `random`. Default values of both those params
are `false`. These params are applicable only to the test execution.

If `practice` is set to `true` then the execution will not record any data. If
`random` is set to `true` then the order of trials in the test will be
randomized.


## Repeating

A flow definition may contain repeat loops. The repeat loop can be specified for
a single test execution or for a block of statements. `repeat` keyword define
the looping statement. There are two form of `repeat`: `repeat <x> times` and
`repeat with`.

### `repeat <x> times`

This form of repeat is used to loop a test or a block of statements for the
given number of times.

Examples:

    repeat 5 times Posner(random true)
    
    repeat 3 times {
        screen Instructions for 10000
        execute Posner
    }
    
`repeat` blocks can be nested:

    repeat 3 times {
        screen Instructions for 10000
        repeat 2 times {
            screen InnerBlockInstructions
            execute Posner
        }
    }



### `repeat with`

This form of looping is used when we have a condition table and we want to
execute a test or a block of statements for each row of the table. Variables
from the table are available inside the looping block.

Example:

    repeat {
        show instruction
        
        // 3 same blocks
        repeat 3 times {
            execute showImages
            show break for 1000
        }
    } with
    | image_type       | order |
    | ---------------- | ----- |
    | image_types loop | 1..2  |


In this example we have a `repeat with` outer loop with a condition table given
after the `with` keyword. `image_types` is a global variable defined, for
example, as:

    image_types = [houses, faces]

used here to [expand the table](condition-tables.md#tables-expansion).

For each row of the table the block of statement will be executed and variables
defined in the table (`image_type` and `order`) will be available inside the
block. These variables will be propagated to all inner repeat loops and to all
execution of tests and screens. This means that we can reference these two
variables in the screen content and in the test expressions (e.g. component
parameters in test definitions).

For a full experiment specification take a look at the [blocking
example](https://github.com/pyflies/pyflies/tree/main/examples/blocking).
