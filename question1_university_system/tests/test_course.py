import unittest
import sqlite3
from question1_university_system.course import Course

class TestCourse(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory DB and sample data before each test"""
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # Create tables
        self.cursor.execute("""
        CREATE TABLE Course (
            course_id INTEGER PRIMARY KEY,
            department_id INTEGER,
            name TEXT,
            credits INTEGER,
            enrollment_limit INTEGER,
            faculty_id INTEGER
        )""")

        self.cursor.execute("""
        CREATE TABLE Enrollment (
            enrollment_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            course_id INTEGER
        )""")

        # Insert a sample course
        self.cursor.execute("""
            INSERT INTO Course (course_id, department_id, name, credits, enrollment_limit, faculty_id)
            VALUES (1, 101, 'Math 101', 3, 30, NULL)
        """)

        # Insert students enrolled in the course
        self.cursor.execute("INSERT INTO Enrollment (enrollment_id, student_id, course_id) VALUES (1, 1001, 1)")
        self.cursor.execute("INSERT INTO Enrollment (enrollment_id, student_id, course_id) VALUES (2, 1002, 1)")

        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_course_initialization(self):
        course = Course(course_id=1, db=self.conn)
        self.assertEqual(course.course_id, 1)
        self.assertEqual(course.department_id, 101)
        self.assertEqual(course.name, "Math 101")
        self.assertEqual(course.credits, 3)
        self.assertEqual(course.enrollment_limit, 30)
        self.assertIsNone(course.faculty_id)
        self.assertEqual(course.enrolled_students, [1001, 1002])

    def test_load_enrolled_students(self):
        course = Course(course_id=1, db=self.conn)
        # Add a new enrollment
        self.cursor.execute("INSERT INTO Enrollment (enrollment_id, student_id, course_id) VALUES (3, 1003, 1)")
        self.conn.commit()
        course.load_enrolled_students()
        self.assertIn(1003, course.enrolled_students)
        self.assertEqual(len(course.enrolled_students), 3)

    def test_assign_faculty_to_course(self):
        course = Course(course_id=1, db=self.conn)
        course.assign_faculty_to_course(faculty_id=10)
        self.assertEqual(course.faculty_id, 10)

        # Check DB update
        self.cursor.execute("SELECT faculty_id FROM Course WHERE course_id=1")
        faculty_id_db = self.cursor.fetchone()[0]
        self.assertEqual(faculty_id_db, 10)

    def test_course_not_found(self):
        with self.assertRaises(ValueError):
            Course(course_id=999, db=self.conn)

if __name__ == "__main__":
    unittest.main()
