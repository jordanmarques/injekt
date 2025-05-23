import inspect
import functools
from typing import Dict, Type, Any, Callable, get_type_hints, TypeVar, cast
import abc

# Registry to store singleton instances
_instances: Dict[Type, Any] = {}

# Type variable for class types
T = TypeVar('T')

def make_singleton(cls: Type[T]) -> Type[T]:
    """
    Internal function to make a class a singleton.
    """
    original_new = cls.__new__

    @functools.wraps(original_new)
    def __new__(cls, *args, **kwargs):
        if cls not in _instances:
            # Call the original __new__ method with just the class
            instance = original_new(cls)
            _instances[cls] = instance
        return _instances[cls]

    cls.__new__ = __new__  # type: ignore
    return cls


def inject(cls_or_func):
    """
    Decorator that can be used on a class or an __init__ method.
    If used on a class, it makes the class a singleton and enables dependency injection.
    If used on an __init__ method, it enables dependency injection for that method.
    """
    # If decorator is applied to a class
    if isinstance(cls_or_func, type):
        cls = cls_or_func

        # Make the class a singleton
        cls = make_singleton(cls)

        # Patch the __init__ method to inject dependencies
        original_init = cls.__init__

        @functools.wraps(original_init)
        def __init__(self, *args, **kwargs):
            # Inject dependencies
            inject_dependencies(original_init, self, *args, **kwargs)

        cls.__init__ = __init__  # type: ignore
        return cls

    # If decorator is applied to a method (assumed to be __init__)
    else:
        init_func = cls_or_func

        @functools.wraps(init_func)
        def wrapper(self, *args, **kwargs):
            # Inject dependencies
            return inject_dependencies(init_func, self, *args, **kwargs)

        return wrapper

def inject_dependencies(init_func, self, *args, **kwargs):
    """
    Helper function to inject dependencies into an __init__ method.
    """
    # Get the type hints for the init function
    type_hints = get_type_hints(init_func)

    # Get the parameter names from the function signature
    signature = inspect.signature(init_func)
    parameters = list(signature.parameters.keys())[1:]  # Skip 'self'

    # Prepare the arguments to inject
    for i, param_name in enumerate(parameters):
        # Skip if the parameter is already provided in args or kwargs
        if i < len(args) or param_name in kwargs:
            continue

        # Get the type hint for this parameter
        if param_name in type_hints:
            param_type = type_hints[param_name]

            # Try to get or create an instance of this type
            if param_type in _instances:
                kwargs[param_name] = _instances[param_type]
            else:
                # Check if there's an instance of a subclass of the required type
                subclass_instance = None
                for cls, instance in _instances.items():
                    if issubclass(cls, param_type) and cls != param_type:
                        subclass_instance = instance
                        break

                if subclass_instance:
                    kwargs[param_name] = subclass_instance
                else:
                    # Check if the parameter type has any subclasses
                    subclasses = param_type.__subclasses__()

                    if subclasses:
                        # Look for concrete implementations of the abstract type
                        concrete_subclasses = []
                        for cls in _instances.keys():
                            if issubclass(cls, param_type) and cls != param_type:
                                concrete_subclasses.append(cls)

                        # Also look for concrete subclasses that aren't in the registry yet
                        for cls in param_type.__subclasses__():
                            if not inspect.isabstract(cls) and cls not in concrete_subclasses:
                                concrete_subclasses.append(cls)

                        if concrete_subclasses:
                            # Use the first concrete implementation found
                            concrete_cls = concrete_subclasses[0]

                            # Create an instance of the concrete implementation
                            instance = concrete_cls()
                            _instances[concrete_cls] = instance
                            kwargs[param_name] = instance
                        else:
                            # No concrete implementation found, raise an error
                            raise TypeError(f"Cannot create an instance of abstract class {param_type.__name__}")
                    else:
                        # Create a new instance and store it in the registry
                        instance = param_type()
                        _instances[param_type] = instance
                        kwargs[param_name] = instance

    # Call the original __init__ with the injected dependencies
    return init_func(self, *args, **kwargs)

# Function to reset the singleton instances (useful for testing)
def reset():
    """
    Reset all singleton instances.
    This is particularly useful for testing to ensure test isolation.
    """
    global _instances
    _instances.clear()

# Export the decorators and utility functions
__all__ = ['inject', 'reset']
