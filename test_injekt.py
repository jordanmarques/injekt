from injekt import inject

# Option 1: Use the @inject decorator on the class
@inject
class PersonService:
    def __init__(self):
        print("PersonService initialized")

    def get_person_name(self):
        return "John Doe"

# Option 1: Use the @inject decorator on the class
@inject
class GroupService:
    def __init__(self, person_service: PersonService):
        self.person_service = person_service
        print("GroupService initialized with", self.person_service)

    def get_group_with_person(self):
        return f"Group with {self.person_service.get_person_name()}"


if __name__ == '__main__':
    # Example usage of the dependency injection framework

    # Create an instance of GroupService
    # PersonService will be automatically injected
    group_service = GroupService()

    # Verify that the PersonService was injected
    print(group_service.get_group_with_person())

    # Verify that we have singletons
    another_group_service = GroupService()
    print("Same instance:", group_service is another_group_service)

    person_service = PersonService()
    print("Same person service:", person_service is group_service.person_service)
