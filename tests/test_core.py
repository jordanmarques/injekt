import pytest
from injekt import inject, reset

# Fixture to reset singleton instances before each test
@pytest.fixture(autouse=True)
def reset_singletons():
    reset()
    yield
    reset()

def test_singleton_behavior():
    """Test that classes decorated with @inject behave as singletons."""
    @inject
    class TestClass:
        def __init__(self):
            self.value = 42

    # Create two instances
    instance1 = TestClass()
    instance2 = TestClass()

    # Check that they are the same instance
    assert instance1 is instance2

    # Check that the instance has the expected value
    assert instance1.value == 42

def test_singleton_instances_are_isolated_between_tests():
    """Test that singleton instances are isolated between tests."""
    @inject
    class TestClass:
        def __init__(self):
            self.value = 42

    # Create an instance and modify it
    instance = TestClass()
    instance.value = 100

    # Reset the singleton instances
    reset()

    # Create a new instance
    new_instance = TestClass()

    # Check that it's a new instance with the default value
    assert new_instance.value == 42

def test_inject_decorator_on_class():
    """Test that the inject decorator on a class makes it a singleton and enables dependency injection."""
    @inject
    class Dependency:
        def __init__(self):
            self.value = 42

    @inject
    class Service:
        def __init__(self, dependency: Dependency):
            self.dependency = dependency

    # Create two instances of Service
    service1 = Service()
    service2 = Service()

    # Check that they are the same instance (singleton behavior)
    assert service1 is service2

    # Check that the dependency was injected
    assert isinstance(service1.dependency, Dependency)
    assert service1.dependency.value == 42

    # Check that the dependency is a singleton
    dependency = Dependency()
    assert service1.dependency is dependency

def test_inject_with_manual_dependency():
    """Test that dependencies can be provided manually."""
    @inject
    class Dependency:
        def __init__(self):
            self.value = 42

    @inject
    class Service:
        def __init__(self, dependency: Dependency):
            self.dependency = dependency

    # Create a custom dependency
    custom_dependency = Dependency()
    custom_dependency.value = 100

    # Create a service with the custom dependency
    service = Service(dependency=custom_dependency)

    # Check that the custom dependency was used
    assert service.dependency is custom_dependency
    assert service.dependency.value == 100

def test_inject_with_multiple_dependencies():
    """Test that multiple dependencies can be injected."""
    @inject
    class DependencyA:
        def __init__(self):
            self.value = "A"

    @inject
    class DependencyB:
        def __init__(self):
            self.value = "B"

    @inject
    class Service:
        def __init__(self, dependency_a: DependencyA, dependency_b: DependencyB):
            self.dependency_a = dependency_a
            self.dependency_b = dependency_b

    # Create a service
    service = Service()

    # Check that both dependencies were injected
    assert isinstance(service.dependency_a, DependencyA)
    assert isinstance(service.dependency_b, DependencyB)
    assert service.dependency_a.value == "A"
    assert service.dependency_b.value == "B"
