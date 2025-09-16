import sqlite3
from typing import List

class Department:
    """
    Department class to manage faculty, courses, and students.
    """
    def __init__(self, department_id: int, db: sqlite3.Connection):
        """
        Initialize a Department.

        Args:
            department_id (int): ID of the department in the database.
            db (sqlite3.Connection): Database connection for student/faculty operations.
        """
        self.department_id = department_id
        self.db = db
        self.faculty: List = []  # List of Faculty objects
        self.courses: List = []  # List of Course objects
        self.students: List = []  # List of Student IDs

        # Load department name from DB
        cursor = self.db.cursor()
        cursor.execute("SELECT name FROM Department WHERE department_id = ?", (department_id,))
        row = cursor.fetchone()
        self.name = row[0] if row else f"Department {department_id}"

    def add_faculty(self, faculty) -> None:
        """
        Add a faculty member to this department.

        Args:
            faculty: Faculty object.

        Returns:
            None
        """
        self.faculty.append(faculty)
        print(f"{faculty.name} has joined the {self.name} department.")

    def add_course(self, course) -> None:
        """
        Add a course to this department.

        Args:
            course: Course object.

        Returns:
            None
        """
        self.courses.append(course)
        print(f"{course.course_code} - {course.course_name} added to {self.name} department.")

    def assign_student_to_department(self, student_id: int) -> None:
        """
        Assign a student to this department in the database and add to in-memory list.

        Args:
            student_id (int): ID of the student.

        Returns:
            None
        """
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE Student
            SET department_id = ?
            WHERE student_id = ?
        """, (self.department_id, student_id))
        self.db.commit()

        # Add student to in-memory list if not already present
        if student_id not in self.students:
            self.students.append(student_id)
        print(f"Student {student_id} assigned to Department {self.name}.")

    def list_courses(self) -> None:
        """
        List all courses in the department.

        Returns:
            None
        """
        for course in self.courses:
            print(course)
