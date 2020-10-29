# Component types

---

Components are internally defined using DSL for component specification.
Currently this DSL is not exposed to end users but we have plan to do so in the
future to support specification of additional components that are not provided
by pyFlies. We must assert that making non-standard components will make
experiment specification non-portable across different target generators but it
could be invaluable in the situations where non-standard components are required
and portability is not an issue.

This page is generated on 2020-10-29 14:51:41 from component descriptions during build so
what is documented here is what pyFlies actually uses:


## base

    // Base abstract components that define common properties

    abstract component visual
    """
    The definition of parameters used by all visual stimuli
    """
    {
        param position:point = (0, 0)
        """
        The position of the component. By default center of the screen.
        """

        param size:[symbol, int] = 20
        """
        The size of the component. May be given in descriptive way or as a
        size in the coordinate space.
        """

        param color:[symbol, color] = #ffffff
        """
        This color is used for border of the component. Default is white.
        """

        param fillColor:[symbol, color] = #ffffff
        """
        This color is used to fill the interior of the visual component.
        Default is white.
        """
    }

    abstract component audible
    """
    This is an abstract component that should be inherited by all components
    that play sounds.
    """
    {}

    abstract component input
    """
    This is an abstract component that should be inherited by all components
    that accepts input from the subject.
    """
    {}


## cross

    component cross extends visual
    """
    Usually used as a fixation point
    """
    {}


## circle

    component circle extends visual
    """
    Visual stimuli in the shape of a circle.
    """
    {
        param radius:int = 20
        """
        The radius of the circle.
        """
    }


## text

    component text extends visual
    """
    A component for displaying text
    """
    {
        param content: string = 'default text'
        """
        A mandatory content for display
        """
    }


## line

    component line extends visual
    """
    Visual stimuli representing line between two points
    """
    {
        param from:[symbol, point] = (-50, 0)
        """
        The start point of the line shape
        """

        param to:[symbol, point] = (50, 0)
        """
        The end point of the line shape
        """
    }


## rectangle

    component rectangle extends visual
    """
    Visual stimuli in the form of rectangle
    """
    {
        param size:[symbol, point] = (20, 20)
        """
        Override `size` to be of point type representing width and height.
        0 for height means 'keep aspect ratio'.
        """
    }


## image

    component image extends visual
    """
    A component that displays image loaded from file
    """
    {
        param file: string = 'default path'
        """
        A file path relative to the model file.
        """

        param ori: int = 0
        """
        Orijentation in degrees.
        """
    }


## audio

    component audio extends audible
    """
    Plays audio loaded from the given file
    """
    {
        param file: string = 'default path'
        """
        The file to load audio from
        """
    }



## sound

    component sound extends audible
    """
    Plays sound of the given frequency
    """
    {
       param freq: int = 500 
       """
       The frequency of the sound
       """
    }


## keyboard

    component keyboard extends input
    """
    Component for implementing keyboard input
    """
    {
        param valid:[symbol, list] = space
        """
        What is considered a valid keystroke in the trial.
        Can be a list of valid keys.
        """

        param correct:[symbol, list] = space
        """
        What is a correct response for this trial.
        Can be a single key or a list of keys.
        If this parameter is provided, must be found in valid list of keys.
        If not given any key from the list of valid keys is considered correct.
        """
    }


## mouse

    component mouse extends input
    """
    Component for implementing mouse input
    """
    {
        param target:[symbol, list] = none
        """
        A component name or a list of component names which represents valid targets.
        If target is none than any click is valid.
        """
    }

