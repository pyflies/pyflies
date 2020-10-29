# Target configuration

---

Target configuration is optional and is used to configure target generator.

It is specified at the end of the experiment and there can be multiple target
configuration as we might have generators for different platforms.

The content of the target block is given in:

    <configuration param> = <value>
    
    
Where configuration parameters are defined by target generator and should be
specified in its documentation.

For example:

    target PsychoPy {
      soundBackend = 'backend_sounddevice.SoundDeviceSound'
      background = grey
      fullScreen = true
    }


See [PsychoPy
generator](https://github.com/pyflies/pyflies-psychopy/blob/main/pfpsychopy/__init__.py#L18)
for one way how configuration parameters and their default values might be
specified.

Beside setting some builtin generator parameter like in the example above,
target configuration can be used to resolve symbols to target-specific values.


    target PsychoPy {
        left = (-0.5, 0)
        right = (0.5, 0)
    }


Also, you can use scoping to provide different mapping of the symbols in
different contexts.

    target PsychoPy {
        left = (-0.5, 0)
        right = (0.5, 0)
        keyboard.left = left
        keyboard.right = right
    }

Here, we want symbol `left` to be mapped to left position on screen but in the
context of keyboard component it will map to key `left`.