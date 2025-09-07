"""
Department class to manage faculty and courses.
"""

class Department:
    def __init__(self, name: str):
        self.name = name
        self.faculty = []  # List of Faculty objects
        self.courses = []  # List of Course objects
        self.students = []  # List of Student objects

    def add_faculty(self, faculty):
        """Add a faculty member to this department."""
        self.faculty.append(faculty)
        print(f"{faculty.name} has joined the {self.name} department.")

    def add_course(self, course):
        """Add a course to this department."""
        self.courses.append(course)
        print(f"{course.course_code} - {course.course_name} added to {self.name} department.")

    def add_student(self, student):
        """Assign a student to this department."""
        self.students.append(student)
        print(f"{student.name} has been added to the {self.name} department.")

    def list_courses(self):
        """List all courses in the department."""
        for course in self.courses:
            print(course)

    def __str__(self):
        return f"Department of {self.name} | Faculty: {len(self.faculty)} | Courses: {len(self.courses)} | Students: {len(self.students)}"
