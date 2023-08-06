from vital.tools import strings as string_tools


__all__ = ('unpythonize', 'pythonize')


def unpythonize(opt):
    try:
        return {string_tools.underscore_to_camel(k): unpythonize(v)
                for k, v in opt.items()}
    except AttributeError:
        return opt


def pythonize(opt):
    try:
        return {string_tools.camel_to_underscore(k): pythonize(v)
                for k, v in opt.items()}
    except AttributeError:
        return opt
