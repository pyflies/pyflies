from .evaluated import EvaluatedBase


class TimeReferenceInst(EvaluatedBase):
    """
    Represents an evaluated time reference specification.
    """
    def __init__(self, spec, context=None):
        super().__init__(spec, context)
        self.time = spec.time.eval(context)
