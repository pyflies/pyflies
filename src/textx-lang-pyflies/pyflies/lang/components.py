from .common import classes as common_classes, ModelElement


class ParamType(ModelElement):
    def reduce(self):
        import pudb;pudb.set_trace()
        self.default = self.default.reduce()


classes = common_classes + [ParamType]
