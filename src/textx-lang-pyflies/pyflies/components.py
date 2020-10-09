from .evaluated import EvaluatedBase


class ComponentTimeInst(EvaluatedBase):
    """
    Represents an evaluated instance of component-time specification
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
        self.component = spec.component.eval(context) if spec.component else None

    def __repr__(self):
        return 'at {} {} for {}'.format(str(self.at), str(self.component),
                                        str(self.duration))


class ComponentInst(EvaluatedBase):
    """
    An evaluated instance of a component.
    """
    def __init__(self, spec, context=None):
        super().__init__(spec, context)
        self._params = {}
        for p in spec.all_params:
            self._params[p.type.name] = p.eval(context)

    @property
    def name(self):
        return self.spec.type.name

    @property
    def params(self):
        return list(self._params.values())

    def __getattr__(self, name):
        try:
            return self._params[name].value
        except KeyError:
            raise AttributeError('"{}" object has no attribute "{}"'.format(
                type(self).__name__, name))

    def __repr__(self):
        return '{}({})'.format(self.spec.type.name, ', '.join([str(x) for x in self.params]))


class ComponentParamInst(EvaluatedBase):
    def __init__(self, spec, context=None):
        super().__init__(spec, context)
        self.value = self.value.eval(context)

    @property
    def name(self):
        return self.type.name

    def __repr__(self):
        return '{} {}'.format(self.spec.type.name, self.value)
