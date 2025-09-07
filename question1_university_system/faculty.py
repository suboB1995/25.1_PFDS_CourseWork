"""
Faculty hierarchy extending from Person.
"""
from person import Person

class Faculty(Person):
    def __init__(self, name: str, age: int, employee_id: str):
        """
        Initialize a faculty member.
        :param employee_id: Unique faculty identifier
        """
        super().__init__(name, age)
        self.employee_id = employee_id

    def get_responsibilities(self) -> str:
        return "Teach courses and mentor students."

    def calculate_workload(self) -> str:
        return "Standard faculty workload."


class Professor(Faculty):
    def __init__(self, name: str, age: int, employee_id: str, department: str):
        """
        Initialize a professor.
        :param department: Academic department
        """
        super().__init__(name, age, employee_id)
        self.department = department

    def get_responsibilities(self) -> str:
        return f"Professor in {self.department}: teach advanced courses, supervise research, publish papers."

    def calculate_workload(self) -> str:
        return "Professors: lectures, research supervision, administrative duties."


class Lecturer(Faculty):
    def __init__(self, name: str, age: int, employee_id: str, subject: str):
        """
        Initialize a lecturer.
        :param subject: Subject taught by the lecturer
        """
        super().__init__(name, age, employee_id)
        self.subject = subject

    def get_responsibilities(self) -> str:
        return f"Lecturer teaching {self.subject}: focus on teaching and grading."

    def calculate_workload(self) -> str:
        return "Lecturers: deliver lectures and grade assignments."


class TeachingAssistant(Faculty):
    def __init__(self, name: str, age: int, employee_id: str, course: str):
        """
        Initialize a teaching assistant.
        :param course: Course they assist in
        """
        super().__init__(name, age, employee_id)
        self.course = course

    def get_responsibilities(self) -> str:
        return f"Teaching Assistant for {self.course}: help students and manage lab sessions."

    def calculate_workload(self) -> str:
        return "TAs: assist in labs, grade assignments, and hold tutorials."