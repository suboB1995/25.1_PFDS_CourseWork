"""
Staff hierarchy extending from Person.
"""
from person import Person

class Staff(Person):
    def __init__(self, name: str, age: int, role: str):
        """
        Initialize a staff member.
        :param role: Role in the university (e.g., Administrative, Technical)
        """
        super().__init__(name, age)
        self.role = role

    def get_responsibilities(self) -> str:
        return f"{self.role} staff: manage administrative tasks and support faculty and students."