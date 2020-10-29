# Running generators

---

You can generate various content from pyFlies experiment specifications. pyFlies
is built using [textX](https://github.com/textX/textX) library and tool for DSL
development in Python so you can query what generators are available using
`textx` command line tools. To see all installed generators issue `textx
list-generators` command:

    $ textx list-generators                   
    any -> dot                    textX[2.3.0.dev0]             Generating dot visualizations from arbitrary models
    textX -> dot                  textX[2.3.0.dev0]             Generating dot visualizations from textX grammars
    textX -> PlantUML             textX[2.3.0.dev0]             Generating PlantUML visualizations from textX grammars
    pyflies -> log                pyflies[0.4.0.dev0]           Generator for log/debug files.
    pyflies -> psychopy           pyflies-psychopy[0.1.0.dev0]  Generator for generating PsychoPy code from pyFlies descriptions


You will see all generators installed in your Python environment. First column
is in `langauge -> target` format and you can see here that we have two
pyFlies generators registered:

- `pyflies -> log` -- produces log file from the `.pf` files and is builtin
  generator of the [pyflies project](https://github.com/pyflies/pyflies). This
  generator is useful for debugging and overview of the course of your
  experiment.
  
- `pyflies -> psychopy` -- this generator produces PsychoPy Python code from
  `.pf` and this generator is provided by [pyflies-psychopy
  project](https://github.com/pyflies/pyflies-psychopy)


To call generator use `textx generate` command:


    textx generate Posner.pf --target log --overwrite
    
    
Here we generate log output from `Posner.pf` pyflies experiment. We use
`--overwrite` to overwrite existing log file.


    textx generate Parity.pf --target psychopy --overwrite
    
    
This will generate PsychoPy Python code (`Parity.py`) from `Parity.pf` pyflies
file.

textX uses pluggable architecture for languages and generators. Additional
generators may be developed independently of the pyFlies project and registered
in the environment by mere installation with `pip`.
