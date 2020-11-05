# Types and expressions

---

pyFlies has a type system with a some usual types you can find in other
languages, but also some types that are useful in the context of experiments
specification. Operations on these types can form complex expressions. You can
use expressions in various places of your experiment specification.


## Types

pyFlies values can be of the following types:

- `bool` - with values of `true` and `false`. You will rarely need to use these
  values directly. They are usually produced as a results of boolean expression
  evaluation. For example, an expression
  
        direction == right
      
  will have a `bool` value
  
- `int` - is an integer number (e.g. `42`)
- `float` - is a float number (e.g. `3.44`)
- `point` - specifies a location in two dimensional space (e.g. `(2, 5)`)
- `color` - specifies a color in a standard CSS like notation where we have a `#`
  prefix and 6 hex digits, 3 groups of 2 digit where each group represents
  `red`, `green` and `blue` component of the color (e.g. `#455a45`). 
- `string` - a string of characters enclosed with quotes (e.g. `"Hello"`).
  Strings content is piped through [Jinja template
  engine](https://jinja.palletsprojects.com/) during evaluation so a powerful
  string interpolation is available. This interpolation is also done for
  [screens](screens.md).
- `list` - a list of values of any type (e.g. `[1, 2, "hi", [true, 2.3], left]`)
- `range` - is a shorthand for definition of a list with consecutive numbers
  (e.g. `1..5`). Usually used for looping in table expansion, or producing a
  random value from a given range (e.g. `1..100 choose`).
- `symbol` - is just a word which might get bound to a value if the variable of
  the same name is available in the context. If not, a symbol can be mapped to a
  value by the compiler. Usually used to express abstract terms. For example:
  
        directions = [left, right]
      
    Here, values in the `directions` list are symbols whose meaning may be
    determined by variables or by the compiler.
  
!!! tip  
  
    When editing colors in the experiment specification in VS Code editor, various
    extension from the VS Code marketplace may help. For example [Color
    Manager](https://marketplace.visualstudio.com/items?itemName=RoyAction.color-manager).

## Expressions

### if

An expression used to provide a value that depend on a condition.
For example:

    left if cue_pos == right else right
    
So, the form is always:

    <value if true> if <condition> else <value if false>

### loop

`loop` expression is used in [table
expansion](condition-tables.md#tables-expansion). Its form is:

    <expression> loop
    
where `expression` evaluates to a list or range.
    
For example:

    [left, right, up, down] loop
    

### Logic

Logic operators are: `or`, `not`, and `and`. `or` and `and` are standard infix
binary operators while `not` is a standard unary prefix operator:

    color == blue and not practice


### Comparison

Comparison operators can compare values. They are used as standard infix binary
operators. Following operators are supported:

- `==` - equal
- `!=` - not equal
- `<=` - less or equals than
- `>=` - greater or equals than
- `>` - greater than
- `<` - less than


### Arithmetic operators

Standard arithmetic operators are supported: `+`, `-`, `*`, `/` and they work as
usual.


### Randomization

Randomization is supported with `choose` and `shuffle` operations. These
operations are given in a postfix form and are applicable only to lists and ranges.

- `choose` will choose a random element from list/range. For example: 

        [red, green, blue] choose
        1..100 choose
      
- `shuffle` will produce a list where elements are in a random order. For example:

        1..100 shuffle

In the current implementation of the compiler all expressions are pre-evaluated
by the compilation process. E.g. random values are predetermined at compile
time, not run-time. This is done to make generator development easier as
otherwise compiler would need to translate all expressions to the target
language expressions. This is an implementation detail that might change in the
future.
