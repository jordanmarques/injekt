import pytest
from injekt import inject, reset

# Fixture to reset singleton instances before each test
@pytest.fixture(autouse=True)
def reset_singletons():
    reset()
    yield
    reset()

def test_mocking_dependencies():
    """Test that dependencies can be mocked for unit testing."""
    # Define a dependency interface
    class Database:
        def get_user(self, user_id):
            # In a real implementation, this would query a database
            raise NotImplementedError("This should be implemented by concrete classes")

    # Define a mock implementation of the dependency
    class MockDatabase(Database):
        def get_user(self, user_id):
            # Return mock data instead of querying a database
            return {"id": user_id, "name": "Mock User"}

    # Define a service that uses the dependency
    @inject
    class UserService:
        def __init__(self, database: Database):
            self.database = database

        def get_user_name(self, user_id):
            user = self.database.get_user(user_id)
            return user["name"]

    # Create a mock database
    mock_database = MockDatabase()

    # Create a service with the mock database
    service = UserService(database=mock_database)

    # Test the service with the mock database
    user_name = service.get_user_name(123)
    assert user_name == "Mock User"

def test_replacing_dependencies_for_testing():
    """Test that dependencies can be replaced for testing."""
    # Define a real dependency
    @inject
    class RealLogger:
        def log(self, message):
            # In a real implementation, this would write to a log file
            pass

    # Define a mock logger that captures log messages
    class MockLogger:
        def __init__(self):
            self.messages = []

        def log(self, message):
            self.messages.append(message)

    # Define a service that uses the logger
    @inject
    class Service:
        def __init__(self, logger: RealLogger):
            self.logger = logger

        def do_something(self):
            self.logger.log("Something was done")
            return True

    # Create a mock logger
    mock_logger = MockLogger()

    # Create a service with the mock logger
    service = Service(logger=mock_logger)

    # Test the service with the mock logger
    result = service.do_something()
    assert result is True
    assert len(mock_logger.messages) == 1
    assert mock_logger.messages[0] == "Something was done"

def test_subclass_injection():
    """Test that a subclass of a dependency is automatically injected."""
    # Define a dependency interface
    class Database:
        def get_user(self, user_id):
            # In a real implementation, this would query a database
            raise NotImplementedError("This should be implemented by concrete classes")

    # Define a concrete implementation of the dependency
    @inject
    class BQDatabase(Database):
        def get_user(self, user_id):
            # Return data from BigQuery
            return {"id": user_id, "name": "BQ User"}

    # Define a service that uses the dependency
    @inject
    class UserService:
        def __init__(self, database: Database):
            self.database = database

        def get_user_name(self, user_id):
            user = self.database.get_user(user_id)
            return user["name"]

    # Create a service without explicitly providing a database
    service = UserService()

    # Test that the service has an instance of BQDatabase injected
    assert isinstance(service.database, BQDatabase)

    # Test that the service works with the injected BQDatabase
    user_name = service.get_user_name(123)
    assert user_name == "BQ User"

