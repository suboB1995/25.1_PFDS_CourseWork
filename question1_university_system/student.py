"""
Student hierarchy extending from Person with course enrollment and GPA tracking.
Secure and validated Student record with private attributes.
Features:
- Private attributes for encapsulation
- Getter methods for safe access
- Course enrollment with limit
- Grade assignment with validation (0.0 - 4.0)
- GPA calculation
- Academic status tracking (Dean's List, Good Standing, Probation)
"""
from person import Person

class Student(Person):
    """
    Base Student class
    """
    def __init__(self, name: str, age: int, student_id: str):
        super().__init__(name, age)
        self.student_id = student_id
        self.courses = {}

class SecureStudentRecord(Student):
    # Maximum number of courses a student can enroll in
    MAX_COURSES = 6

    def __init__(self, name: str, age: int, student_id: str):
        """
        Initialize a secure student record.
        :param name: Name of the student
        :param age: Age of the student
        :param student_id: Unique student identifier
        """
        super().__init__(name, age)
        self.__student_id = student_id       # Private attribute for student ID
        self.__courses = {}                  # Private dictionary to store courses and grades

    # ---------------- Getters ----------------
    @property
    def student_id(self):
        """Return the student ID (read-only)."""
        return self.__student_id

    @property
    def courses(self):
        """Return a copy of enrolled courses to prevent direct modification."""
        return self.__courses.copy()

    # ---------------- Enrollment ----------------
    def enroll_course(self, course_name: str):
        """
        Enroll the student in a new course.
        Checks for duplicates and maximum course limit.
        """
        if len(self.__courses) >= SecureStudentRecord.MAX_COURSES:
            print(f"{self.name} cannot enroll in more than {SecureStudentRecord.MAX_COURSES} courses.")
            return
        if course_name in self.__courses:
            print(f"{self.name} is already enrolled in {course_name}.")
            return
        self.__courses[course_name] = None  # Grade not yet assigned
        print(f"{self.name} has enrolled in {course_name}.")

    def drop_course(self, course_name: str):
        """
        Drop a course if the student is enrolled in it.
        """
        if course_name in self.__courses:
            del self.__courses[course_name]
            print(f"{self.name} has dropped {course_name}.")
        else:
            print(f"{self.name} is not enrolled in {course_name}.")

    # ---------------- GPA Calculation ----------------
    def calculate_gpa(self) -> float:
        """
        Calculate GPA across all courses with grades.
        Ensures only valid grades (0.0 - 4.0) are considered.
        Invalid grades are ignored with a warning.
        """
        graded_courses = []
        for course, grade in self.courses.items():
            if grade is None:
                continue  # skip courses without grades
            if 0.0 <= grade <= 4.0:
                graded_courses.append(grade)
            else:
                print(f"Warning: Invalid grade {grade} for course '{course}' ignored in GPA calculation.")

        if not graded_courses:
            return 0.0  # no valid grades, GPA is 0.0

        return sum(graded_courses) / len(graded_courses)

    # ---------------- Academic Status ----------------
    def get_academic_status(self) -> str:
        """
        Determine academic status based on GPA:
        - GPA >= 3.5 → Dean's List
        - GPA < 2.0 → Probation
        - Else → Good Standing
        """
        gpa = self.calculate_gpa()
        if gpa >= 3.5:
            return "Dean's List"
        elif gpa < 2.0:
            return "Probation"
        else:
            return "Good Standing"


    # ---------- Polymorphism ----------
    def get_responsibilities(self) -> str:
        """Student-specific responsibilities."""
        return "Attend classes, complete assignments, and study for exams."


class UndergraduateStudent(SecureStudentRecord):
    """
    Undergraduate student with major information.
    """
    def __init__(self, name, age, student_id, major):
        super().__init__(name, age, student_id)
        self.major = major

    def get_responsibilities(self) -> str:
        return f"Undergraduate responsibilities: focus on {self.major} courses."


class GraduateStudent(SecureStudentRecord):
    """
    Graduate student with thesis information.
    """

    def __init__(self, name, age, student_id, thesis_title):
        super().__init__(name, age, student_id)
        self.thesis_title = thesis_title

    def get_responsibilities(self) -> str:
        return f"Graduate responsibilities: research and work on thesis '{self.thesis_title}'."
