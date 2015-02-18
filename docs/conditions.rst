Conditions
##########

pyFlies is based on the condition-stimuli-response paradigm. Each test
description must specify a fixed set of conditions given in `conditions`
section. For each condition a single response is expected.

Conditions section is given as a table where first row represents the name of
the condition variables whose values are given in the corresponding columns of
the subsequent rows.
The name of the variables are arbitrary but one of them should be `response`.
There is no constraint on how many condition variable can be specified or how
many values for each variable can be given.

For example::

  conditions {
      position    color   congruency    response

      left        green   congruent     left
      left        red     incongruent   right
      right       green   incongruent   left
      right       red     congruent     right
  }

In this example there is two independent condition variables (`position` and
`color`) with two possible value each, forming in total 4 conditions. Third
variable `congruency` is dependent and is given here just for the convenience.
The last one `response` is mandatory and gives an abstract representation of the
expected response. This abstract representation is mapped to concrete platform
specific representation by the target configuration.

The values of condition variables can be used in stimuli definition to
parametrize stimuli.

