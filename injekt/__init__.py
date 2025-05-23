import inspect
import functools
from typing import Dict, Type, Any, Callable, get_type_hints, TypeVar, cast

# Registry to store singleton instances
_instances: Dict[Type, Any] = {}

# Type variable for class types
T = TypeVar('T')

def singleton(cls: Type[T]) -> Type[T]:
    """
    Decorator to make a class a singleton.
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
    # Mark the class as a singleton
    setattr(cls, '__injekt_singleton__', True)
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
        singleton_cls = singleton(cls)

        # Patch the __init__ method to inject dependencies
        original_init = cls.__init__

        @functools.wraps(original_init)
        def __init__(self, *args, **kwargs):
            # Inject dependencies
            inject_dependencies(original_init, self, *args, **kwargs)

        cls.__init__ = __init__  # type: ignore
        return singleton_cls

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
                # Create a new instance and store it in the registry
                # If the class is not already a singleton, make it one
                if not hasattr(param_type, '__injekt_singleton__'):
                    param_type = singleton(param_type)

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
__all__ = ['inject', 'singleton', 'reset']
