from .evaluated import EvaluatedBase


class ComponentTimeInst(EvaluatedBase):
    """
    Represents an evaluated instance of component-time specification
    """
    def __init__(self, spec, context=None, last_comp=None):
        super().__init__(spec, context)
        spec.inst = self
        self.at = spec.at.eval(context).time
        if spec.at.relative_op == '-':
            self.at = -self.at
        relative_to = spec.at.relative_to or last_comp
        if relative_to:
            relative = (spec.at.relative_op is not None
                        or spec.at.start_relative
                        or spec.at.relative_to)
            if relative:
                self.at += relative_to.inst.at
                if not spec.at.start_relative:
                    self.at += relative_to.inst.duration
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
