"""
Base class for all people in the university system.
"""
class Person:
    def __init__(self, name: str, age: int):
        """
        Initialize a person with basic attributes.
        :param name: Name of the person
        :param age: Age of the person
        """
        self.name = name
        self.age = age

    def get_responsibilities(self) -> str:
        """
        Base method for responsibilities.
        Can be overridden by subclasses.
        """
        return "General responsibilities for a person."