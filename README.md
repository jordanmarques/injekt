# Injekt: Lightweight Dependency Injection Library for Python

<img src="injekt.png" alt="Injekt Logo" width="300">

## Overview

This project is a lightweight and easy-to-use Dependency Injection (DI) library for Python, designed to simplify the
process of managing dependencies in your application. The library provides an intuitive and powerful way to handle
dependencies, promoting better code organization, improved testability, and a clean separation of concerns.

## Features

- **Lightweight and Fast**: Minimal overhead while providing essential DI functionality.
- **Easy to Use**: Simple and intuitive API for managing dependencies.
- **Flexible**: Supports injection of both classes and simple objects.
- **Test Friendly**: Simplifies mocking dependencies for testing purposes.
- **No Third-Party Dependencies**: Fully self-contained implementation without relying on external packages.

## Installation

To install the library, use the following command:

```bash
pip install injekt
```


## Getting Started

### Basic Usage

Injekt provides a simple way to manage dependencies in your Python applications. Here's how to use it:

1. Import the necessary components:

```python
from injekt import inject
```

2. Define your service classes using the `@inject` decorator on the class:

```python
# Use @inject on the class (automatically makes it a singleton)
@inject
class PersonService:
    def __init__(self):
        print("PersonService initialized")

    def get_person_name(self):
        return "John Doe"

@inject
class GroupService:
    def __init__(self, person_service: PersonService):
        self.person_service = person_service
        print("GroupService initialized with", self.person_service)

    def get_group_with_person(self):
        return f"Group with {self.person_service.get_person_name()}"
```

4. Use your services:

```python
# Create an instance of GroupService
# PersonService will be automatically injected
group_service = GroupService()

# Use the injected dependency
print(group_service.get_group_with_person())  # Output: Group with John Doe
```

### Key Features

#### Automatic Dependency Injection

Injekt automatically injects dependencies based on type hints in your constructor parameters. You don't need to manually create and pass dependencies.

#### Singleton Pattern

All classes managed by Injekt are singletons by default. This means that only one instance of each class will be created and reused throughout your application:

```python
# These will be the same instance
service1 = PersonService()
service2 = PersonService()
print(service1 is service2)  # Output: True
```

#### Type-Based Injection

Injekt uses Python's type hints to determine which dependencies to inject. Make sure to properly annotate your constructor parameters with the correct types.

### Unit Testing with Injekt

Injekt is designed to be compatible with unit testing. Here's how to use it in your tests:

#### Resetting Singleton Instances

When writing unit tests, you often want to start with a clean state for each test. Injekt provides a `reset` function that clears all singleton instances:

```python
import pytest
from injekt import reset

@pytest.fixture(autouse=True)
def reset_singletons():
    # Reset the singleton instances before each test
    reset()
    yield
    # Reset again after the test
    reset()
```

#### Mocking Dependencies

You can easily mock dependencies by passing them explicitly to the constructor:

```python
# Define a mock implementation
class MockDatabase:
    def get_user(self, user_id):
        return {"id": user_id, "name": "Mock User"}

# Create a service with the mock dependency
service = UserService(database=MockDatabase())

# Test the service with the mock dependency
user_name = service.get_user_name(123)
assert user_name == "Mock User"
```

#### Example Test Case

Here's a complete example of a test case:

```python
import pytest
from injekt import inject, reset

# Fixture to reset singleton instances before each test
@pytest.fixture(autouse=True)
def reset_singletons():
    reset()
    yield
    reset()

def test_get_user_name():
    # Define a mock database
    class MockDatabase:
        def get_user(self, user_id):
            return {"id": user_id, "name": "Mock User"}

    # Define the service
    @inject
    class UserService:
        def __init__(self, database):
            self.database = database

        def get_user_name(self, user_id):
            user = self.database.get_user(user_id)
            return user["name"]

    # Create a service with the mock database
    service = UserService(database=MockDatabase())

    # Test the service
    assert service.get_user_name(123) == "Mock User"
```

## Contributing

Contributions are welcome! If you'd like to contribute to the development of this library:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m "Description of the feature"`.
4. Push to the branch: `git push origin feature-name`.
5. Open a Pull Request.

## License

This project is released under the [MIT License](LICENSE). Feel free to use it in your own projects!

---

Thank you for using this Dependency Injection library. Happy coding!
