# Running generators

---

You can generate various content from pyFlies experiment specifications. pyFlies
is built using [textX](https://github.com/textX/textX) tool for DSL development
in Python so you can query what generators are available using `textx` command
line tools. To see all installed generators use `textx list-generators` command:

    $ textx list-generators                   
    any -> dot                    textX[2.3.0.dev0]             Generating dot visualizations from arbitrary models
    textX -> dot                  textX[2.3.0.dev0]             Generating dot visualizations from textX grammars
    textX -> PlantUML             textX[2.3.0.dev0]             Generating PlantUML visualizations from textX grammars
    pyflies -> log                pyflies[0.4.0.dev0]           Generator for log/debug files.
    pyflies -> csv                pyflies[0.4.0.dev0]           Generator for CSV files from pyFlies tables.
    pyflies -> psychopy           pyflies-psychopy[0.1.0.dev0]  Generator for generating PsychoPy code from pyFlies descriptions


You will see all generators installed in your Python environment. First column
is in `language -> target` format and you can see here that we have three
pyFlies generators registered:

- `pyflies -> log` -- produces log files from `.pf` files and is a builtin
  generator of the [pyflies project](https://github.com/pyflies/pyflies). This
  generator is useful for debugging and overview of the course of your
  experiment.
  
- `pyflies -> csv` -- produces CSV files from condition tables specified in
  `.pf` files and is also a builtin generator provided by the [pyflies
  project](https://github.com/pyflies/pyflies). This generator is useful if you
  want a quick way to produce CSV condition files to be used in other experiment
  tools.
  
- `pyflies -> psychopy` -- this generator produces PsychoPy Python code from
  `.pf` and is provided by [pyflies-psychopy
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
