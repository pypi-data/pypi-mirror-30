import json


class LanguageSpecification:
    def __getitem__(self, item):
        if not item:
            item = "nop"
        return getattr(self, f"function_{item}")


class BuiltinLanguage(LanguageSpecification):
    def function_nop(self, value, evaluator, context):
        return evaluator(value, context)

    def function_sum(self, value, evaluator, context):
        return sum(evaluator(v, context) for v in value)


class Evaluator:
    def __init__(self, language_spec):
        self.language = language_spec()

    def __call__(self, expr, context=None):
        if context is None:
            context = {}

        if isinstance(expr, dict):
            expression_keys = [k for k in expr if k.startswith("=")]
            if len(expression_keys) != 1:
                raise ValueError("Invalid expression")

            key = expression_keys[0]
            value = expr[key]

            if isinstance(value, dict):
                value = self(value, context)

            func = self.language[key[1:]]
            return func(value, self, context)

        if isinstance(expr, (list, tuple)):
            return [self(v, context) for v in expr]

        if isinstance(expr, str):
            if expr.startswith("@{") and expr.endswith("}"):
                return eval(expr[2:-1], {}, context)
            return expr.format(**context)

        return expr


dicteval = Evaluator(BuiltinLanguage)


def jsoneval(string):
    return dicteval(json.loads(string))
