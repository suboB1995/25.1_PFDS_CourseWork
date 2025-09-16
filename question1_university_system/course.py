import sqlite3

class Course:
    """
    Course class reflecting updated database schema with enrollment limits and faculty assignment.
    """
    def __init__(self, course_id: int, db: sqlite3.Connection):
        """
        Initialize a Course object from database.

        Args:
            course_id (int): ID of the course in the DB.
            db (sqlite3.Connection): Database connection.
        """
        self.course_id = course_id
        self.db = db
        self.enrolled_students = []

        cursor = self.db.cursor()
        cursor.execute("""
            SELECT department_id, name, credits, enrollment_limit, faculty_id
            FROM Course
            WHERE course_id = ?
        """, (course_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Course with ID {course_id} not found in DB.")

        self.department_id, self.name, self.credits, self.enrollment_limit, self.faculty_id = row

        # Load enrolled students
        self.load_enrolled_students()

    def load_enrolled_students(self):
        """Load currently enrolled students from DB."""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT student_id
            FROM Enrollment
            WHERE course_id = ?
        """, (self.course_id,))
        self.enrolled_students = [row[0] for row in cursor.fetchall()]

    def assign_faculty_to_course(self, faculty_id: int):
        """
        Assign a faculty member to this course.

        Args:
            faculty_id (int): ID of the faculty member.

        Returns:
            None
        """
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE Course
            SET faculty_id = ?
            WHERE course_id = ?
        """, (faculty_id, self.course_id))
        self.db.commit()
        self.faculty_id = faculty_id
        print(f"Faculty {faculty_id} assigned to Course {self.name}.")
