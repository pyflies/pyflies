class EvaluatedBase:
    """
    Base class for all evaluated instances.  All evaluated attributes are
    accessible directly on the object, others are delegated to the spec object.
    """
    def __init__(self, spec):
        self.spec = spec

    def __getattr__(self, name):
        return getattr(self.spec, name)
