# Condition tables

---

Condition tables define one or more variables in each column and their values
for conditions in each row. They are used to specify values of related variables
given in a row representing a certain state.

These tables are used in [test defintion](test.md) and for [repeat
with](flow.md#repeat-with) form of repetition.

In the test definition each row of the table represent a single test trial.
While in `repeat with` statement each row represent a single cycle through the
repeat loop where the values of the variables will be from the corresponding
table row.

    | number       | parity   |
    |--------------|----------|
    | numbers loop | parities |

The header of the table contains variable names (`number` and `parity`) while
the cells of the rest of the table contain
[expressions](types-expressions.md#expressions).


## Tables expansion

Tables are usually, although not necessary, written in a compact form which is
expanded during compilation. This compact representation is shorter, require
less screen space and gives more flexibility in adding new variables and
altering the number of conditions.

!!! note

    Tables are written in pure text and can be edited with any text editor 
    but for a convenience pyFlies VS Code editor has auto-formatting and 
    navigation capabilities which makes editing much more pleasant.

To understand table expansion lets look at some examples. Lets say we want to
loop through several colors and for each color to loop through some directions
to explore all possible options. We can do that in the following way:

    | color                   | direction          |
    | ----------------------- | ------------------ |
    | [red, green, blue] loop | [left, right] loop |


Expressions in both columns are `loop` expressions over list of symbols. Loop
expressions are evaluated and nested from left to right, so the table in
expanded form will be:

    | color | direction |
    | ----- | --------- |
    | red   | left      |
    | red   | right     |
    | green | left      |
    | green | right     |
    | blue  | left      |
    | blue  | right     |
    

!!! tip

    Use [log generator](generators.md) to produce expanded tables, and other interesting
    information about your experiment.

Now, lets expand the table a bit. Lets suppose that we want a new table variable
called `congruency` that has value `congruent` if color is `green` and
`incongruent` otherwise. For this we can use `if` expression:

    | color                   | direction          | congruency                                   |
    | ----------------------- | ------------------ | -------------------------------------------- |
    | [red, green, blue] loop | [left, right] loop | congruent if color == green else incongruent |

See how we referenced `color` variable in the `congruency` column and compared
its value with the symbol `green`.

Now, the expanded table will be:

    | color | direction | congruency  |
    | ----- | --------- | ----------- |
    | red   | left      | incongruent |
    | red   | right     | incongruent |
    | green | left      | congruent   |
    | green | right     | congruent   |
    | blue  | left      | incongruent |
    | blue  | right     | incongruent |
    

!!! tip

    To make table expressions simpler you can always define variables which can hold
    a used sequence or a whole expression. For example:

        colors = [red, green, blue]
        directions = [left, right]
        is_congruent = congruent if color == green else incongruent

        test MyTest {

            | index | color       | direction       | congruency   |
            | ----- | ----------- | --------------- | ------------ |
            | 1..8  | colors loop | directions loop | is_congruent |

        }


Now, lets say we want to introduce `index` variable which will be the number of
the current row. In compact form it is easy:

    | index | color                   | direction          | congruency                                   |
    | ----- | ----------------------- | ------------------ | -------------------------------------------- |
    | 1..8  | [red, green, blue] loop | [left, right] loop | congruent if color == green else incongruent |

Notice the use of the [range type](types-expressions.md) as the expression in
the `index` column. If we have a sequence-like type (list or range) then the
value will cycle, i.e. for each row the next value from the sequence will be
used until the sequence is exhausted. After that the sequence will start from
the beginning. So, we can say that `loop` expression take precedence. If the row
has loop expressions they will be used, from left to right, to drive the row
creation and other sequences will be fillers. If no loop exists in the row,
sequences will expand until the longest is exhausted.

Consider this example:

    | color              | direction     |
    | ------------------ | ------------- |
    | [red, green, blue] | [left, right] |

Since we have no loops the table will expand to three rows, until the colors are
exhausted while the direction will cycle:

    | color | direction |
    | ----- | --------- |
    | red   | left      |
    | green | right     |
    | blue  | left      |

In the previous example where we added `index` column with range `1..8`, we
could easily specify larger range `1..100` and the result will be the same. That
is because we have loops in the column and the `index` is just the filler so
that after row `8` is created all loops are over and the expansion stops.

We can specify multiple rows even in a compact form, and can mix and match
constant rows with expression based. For example:

    | index  | color                   | direction          |
    | ------ | ----------------------- | ------------------ |
    | 1..2   | [orange, brown]         | up                 |
    | 3..100 | [red, green, blue] loop | [left, right] loop |

will expand to:

    | index | color  | direction |
    |-------|--------|-----------|
    | 1     | orange | up        |
    | 2     | brown  | up        |
    | 3     | red    | left      |
    | 4     | red    | right     |
    | 5     | green  | left      |
    | 6     | green  | right     |
    | 7     | blue   | left      |
    
So, the first row will expand and then the second.

Now, you can see that creating table of conditions is easy and very powerful.

!!! tip

    pyFlies provides CSV generator, which is a standard textX based generator
    like all others, that you can use to create condition table using
    pyFlies powerful syntax and table expansion and export it for use in other
    tools.
