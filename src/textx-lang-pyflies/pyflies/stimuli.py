from .evaluated import EvaluatedBase


class StimulusSpecInst(EvaluatedBase):
    """
    Represents an evaluated instance of stimulus specification
    """
    def __init__(self, spec, context=None, last_stim=None):
        super().__init__(spec, context)
        self.at = spec.at.eval(context).time
        if self.spec.at.relative_op == '-':
            self.at = -self.at
        if last_stim:
            relative = self.spec.at.relative_op is not None or self.spec.at.start_relative
            if relative:
                self.at += last_stim.at
                if not self.spec.at.start_relative:
                    self.at += last_stim.duration
        self.duration = spec.duration.eval(context)
        self.stimulus = spec.stimulus.eval(context) if spec.stimulus else None

    def __repr__(self):
        return 'at {} {} for {}'.format(str(self.at), str(self.stimulus),
                                        str(self.duration))


class StimulusInst(EvaluatedBase):
    """
    An evaluated instance of stimulus
    """
    def __init__(self, spec, context=None):
        super().__init__(spec, context)
        self.params = []
        for p in spec.params:
            self.params.append(p.eval(context))

    def __repr__(self):
        return '{}({})'.format(self.spec.name, ', '.join([str(x) for x in self.params]))


class StimulusParamInst(EvaluatedBase):
    def __init__(self, spec, context=None):
        super().__init__(spec, context)
        self.value = self.value.eval(context)

    def __repr__(self):
        return '{} {}'.format(self.spec.name, self.value)
