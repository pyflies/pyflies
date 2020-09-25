class TimeReferenceInst:
    """
    Represents an evaluated time reference specification.
    """
    def __init__(self, spec, context=None):
        self.spec = spec
        self.time = spec.time.eval(context)

    def __getattr__(self, name):
        return getattr(self.spec, name)
