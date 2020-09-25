from .evaluated import EvaluatedBase


class StimulusSpecInst(EvaluatedBase):
    """
    Represents an evaluated instance of stimulus specification
    """
    def __init__(self, spec, context=None):
        super().__init__(spec, context)
        self.at = spec.at.eval(context)
        self.duration = spec.duration.eval(context)
        self.stimulus = spec.stimulus.eval(context) if spec.stimulus else None


class StimulusInst(EvaluatedBase):
    """
    An evaluated instance of stimulus
    """
    def __init__(self, spec, context=None):
        super().__init__(spec, context)
        self.params = []
        for p in spec.params:
            self.params.append(p.eval(context))


class StimulusParamInst(EvaluatedBase):
    def __init__(self, spec, context=None):
        super().__init__(spec, context)
