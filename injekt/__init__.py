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

def _find_subclass_instance(param_type):
    """
    Find an instance of a subclass of the required type in the registry.

    Args:
        param_type: The type to find a subclass instance for

    Returns:
        An instance of a subclass if found, None otherwise
    """
    for cls, instance in _instances.items():
        if issubclass(cls, param_type) and cls != param_type:
            return instance
    return None

def _get_concrete_subclasses(param_type):
    """
    Get a list of concrete subclasses of an abstract type.

    Args:
        param_type: The abstract type to find concrete subclasses for

    Returns:
        A list of concrete subclass types
    """
    concrete_subclasses = []

    # Look for concrete implementations in the registry
    for cls in _instances.keys():
        if issubclass(cls, param_type) and cls != param_type:
            concrete_subclasses.append(cls)

    # Also look for concrete subclasses that aren't in the registry yet
    for cls in param_type.__subclasses__():
        if not inspect.isabstract(cls) and cls not in concrete_subclasses:
            concrete_subclasses.append(cls)

    return concrete_subclasses

def _create_and_register_instance(cls):
    """
    Create an instance of a class and register it as a singleton.

    Args:
        cls: The class to instantiate

    Returns:
        The created instance
    """
    instance = cls()
    _instances[cls] = instance
    return instance

def _get_or_create_instance(param_type):
    """
    Get an existing instance or create a new one.

    Args:
        param_type: The type to get or create an instance for

    Returns:
        An instance of the specified type
    """
    # Check if we already have an instance
    if param_type in _instances:
        return _instances[param_type]

    # Check if there's an instance of a subclass
    subclass_instance = _find_subclass_instance(param_type)
    if subclass_instance:
        return subclass_instance

    # Check if the parameter type has any subclasses
    subclasses = param_type.__subclasses__()
    if subclasses:
        concrete_subclasses = _get_concrete_subclasses(param_type)

        if concrete_subclasses:
            # Use the first concrete implementation found
            concrete_cls = concrete_subclasses[0]
            return _create_and_register_instance(concrete_cls)
        else:
            # No concrete implementation found, raise an error
            raise TypeError(f"Cannot create an instance of abstract class {param_type.__name__}")
    else:
        # Create a new instance and store it in the registry
        return _create_and_register_instance(param_type)

def _inject_parameter(param_name, param_type, kwargs):
    """
    Inject a parameter into kwargs if not already present.

    Args:
        param_name: The name of the parameter
        param_type: The type of the parameter
        kwargs: The keyword arguments to inject into
    """
    kwargs[param_name] = _get_or_create_instance(param_type)

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
            _inject_parameter(param_name, param_type, kwargs)

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
