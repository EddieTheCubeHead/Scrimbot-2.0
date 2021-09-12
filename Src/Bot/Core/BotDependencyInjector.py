__version__ = "0.1"
__author__ = "Eetu Asikainen"

from inspect import signature, Parameter
from typing import Type, get_args, Union, Any

from Bot.Exceptions.BuildException import BuildException


def _is_injectable_argument(arg):
    return arg.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.POSITIONAL_ONLY) and arg.default is Parameter.empty


def _is_method_target_argument(arg):
    return arg.name in ("self", "cls")


# Used for differentiating instance dependencies from singleton dependencies in dependency dict
class InstanceSentinel:
    pass


class BotDependencyInjector:

    dependencies: dict[type, Any] = {}

    def __init__(self, db_master_connection):
        self._db_master_connection = db_master_connection

    @classmethod
    def singleton(cls, dependency_class: type):
        cls._add_dependency(dependency_class, None)
        return dependency_class

    @classmethod
    def instance(cls, dependency_class: type):
        cls._add_dependency(dependency_class, InstanceSentinel())
        return dependency_class

    @classmethod
    def _add_dependency(cls, dependency_class: type, default_value: Union[None, InstanceSentinel]):
        if dependency_class in cls.dependencies:
            raise BuildException(f"Could not register dependency {dependency_class.__name__} as a dependency with"
                                 f" identical name already exists.")
        cls.dependencies[dependency_class] = default_value

    @classmethod
    def inject(cls, func):
        def injection_wrapper(*args, **kwargs):
            return cls._inject_needed(func, *args, **kwargs)

        return injection_wrapper

    @classmethod
    def _inject_needed(cls, func, *args, **kwargs):
        func_args = signature(func)
        injected = []
        for arg in list(func_args.parameters.values())[len(args):]:
            if _is_injectable_argument(arg) and not _is_method_target_argument(arg):
                injected += [cls._inject_arg(arg)]
        return func(*args, *injected, **kwargs)

    @classmethod
    def _inject_arg(cls, arg):
        if arg.annotation == Parameter.empty:
            raise (BuildException(f"Could not inject argument {arg} because it doesn't have a type annotation."))
        real_key = cls._is_dependency_present(arg.annotation)
        if real_key:
            return cls._get_dependency(real_key)
        raise (BuildException(f"Could not inject argument {arg.name} because type '{arg.annotation}' is not registered "
                              f"as a dependency."))

    @classmethod
    def _is_dependency_present(cls, annotation):
        if annotation in cls.dependencies:
            return annotation
        for dependency in cls.dependencies:
            if annotation == str(dependency).split(".")[-1][:-2]:
                return dependency
        return None

    @classmethod
    def _get_dependency(cls, annotation):
        if type(cls.dependencies[annotation]) is InstanceSentinel:
            return annotation()
        if not cls.dependencies[annotation]:
            cls.dependencies[annotation] = annotation()
        return cls.dependencies[annotation]
