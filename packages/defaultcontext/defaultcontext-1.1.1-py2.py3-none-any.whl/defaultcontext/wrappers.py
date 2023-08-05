import functools
import warnings

from .stack import DefaultStack


class _DefaultContextMixin(object):
    def as_default(self):
        return self.__class__.set_default(self)

    @classmethod
    def get_default(cls):
        instance = cls._default_stack.get_default()

        # Lazily construct default instance when first requested
        if instance is None and not hasattr(cls, "_global_default_instance") \
                    and cls._global_default_factory is not None:
            maybe_default_instance = None
            try:
                maybe_default_instance = cls._global_default_factory()
            except TypeError:
                # Fix for Python 2 unbounded method error
                maybe_default_instance = cls._global_default_factory.__func__()
            instance = cls._global_default_instance = maybe_default_instance

        # Case when instance is None, but global default is already built
        elif instance is None and hasattr(cls, "_global_default_instance"):
            instance = cls._global_default_instance

        return instance

    @classmethod
    def set_default(cls, instance):
        return cls._default_stack.get_context_manager(instance)

    @classmethod
    def set_global_default(cls, instance):
        cls._global_default_instance = instance

    @classmethod
    def reset_defaults(cls):
        cls._default_stack.reset()
        delattr(cls, "_global_default_instance")


def optional_arg_class_decorator(fn):
    """
    Based on:
    https://stackoverflow.com/questions/3888158/python-making-decorators-with-optional-arguments
    """
    @functools.wraps(fn)
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and isinstance(args[0], type) and not kwargs:
            return fn(args[0])
        else:
            def real_decorator(decoratee):
                return fn(decoratee, *args, **kwargs)
            return real_decorator
    return wrapped_decorator


@optional_arg_class_decorator
def with_default_context(cls,
        use_empty_init=False,
        global_default_factory=None):
    """
    :param use_empty_init: If set to True, object constructed without
            arguments will be a global default object of the class.
    :param global_default_factory: Function that constructs a global
            default object of the class.

    N.B. Either `use_empty_init` should be set to True, or the
    `global_default_factory` should be passed, but not both.
    """

    if use_empty_init:
        if global_default_factory is not None:
            warnings.warn("Either factory or use_empty_init should be set. "
                          "Assuming use_empty_init=True.")
        global_default_factory = lambda: cls()

    class_attrs = dict(_default_stack=DefaultStack(),
                       _global_default_factory=global_default_factory)
    class_attrs.update(cls.__dict__)
    return type(cls.__name__, (cls, _DefaultContextMixin), class_attrs)

