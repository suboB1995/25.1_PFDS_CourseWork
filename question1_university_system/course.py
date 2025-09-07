"""
Course class with enrollment limits and prerequisite checking.
"""

class Course:
    def __init__(self, course_code: str, course_name: str, max_students: int, prerequisites=None):
        """
        Initialize a course.
        :param course_code: Unique code (e.g., CS101)
        :param course_name: Human-readable name
        :param max_students: Maximum allowed students
        :param prerequisites: List of prerequisite course codes
        """
        self.course_code = course_code
        self.course_name = course_name
        self.max_students = max_students
        self.prerequisites = prerequisites if prerequisites else []
        self.enrolled_students = []  # List of student objects
        self.assigned_faculty = None  # Faculty object

    def assign_faculty(self, faculty):
        """Assign a faculty member to teach this course."""
        self.assigned_faculty = faculty
        print(f"{faculty.name} has been assigned to teach {self.course_code} - {self.course_name}.")

    def enroll_student(self, student):
        """Enroll a student if capacity and prerequisites allow."""
        # Check limit
        if len(self.enrolled_students) >= self.max_students:
            print(f"Enrollment failed: {self.course_code} is full.")
            return False

        # Check prerequisites
        for prereq in self.prerequisites:
            if prereq not in student.courses or student.courses[prereq] is None or student.courses[prereq] < 2.0:
                print(f"Enrollment failed: {student.name} has not met prerequisite {prereq}.")
                return False

        self.enrolled_students.append(student)
        student.enroll_course(self.course_code)
        print(f"{student.name} successfully enrolled in {self.course_code}.")
        return True

    def __str__(self):
        faculty_name = self.assigned_faculty.name if self.assigned_faculty else "Unassigned"
        return f"{self.course_code}: {self.course_name} | Faculty: {faculty_name} | Enrolled: {len(self.enrolled_students)}/{self.max_students}"
