import unittest
import sqlite3
from question1_university_system.department import Department

# Dummy classes to simulate Faculty and Course
class DummyFaculty:
    def __init__(self, name):
        self.name = name

class DummyCourse:
    def __init__(self, course_code, course_name):
        self.course_code = course_code
        self.course_name = course_name
    def __repr__(self):
        return f"{self.course_code} - {self.course_name}"

class TestDepartment(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory DB and tables before each test"""
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # Create tables
        self.cursor.execute("""
        CREATE TABLE Department (
            department_id INTEGER PRIMARY KEY,
            name TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE Student (
            student_id INTEGER PRIMARY KEY,
            name TEXT,
            department_id INTEGER
        )""")

        # Insert sample department
        self.cursor.execute("INSERT INTO Department (department_id, name) VALUES (1, 'Computer Science')")
        self.cursor.execute("INSERT INTO Student (student_id, name, department_id) VALUES (1001, 'Nimal', NULL)")
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_department_initialization(self):
        dept = Department(1, self.conn)
        self.assertEqual(dept.department_id, 1)
        self.assertEqual(dept.name, "Computer Science")
        self.assertEqual(dept.faculty, [])
        self.assertEqual(dept.courses, [])
        self.assertEqual(dept.students, [])

    def test_add_faculty(self):
        dept = Department(1, self.conn)
        faculty = DummyFaculty("Dr. Namal")
        dept.add_faculty(faculty)
        self.assertIn(faculty, dept.faculty)

    def test_add_course(self):
        dept = Department(1, self.conn)
        course = DummyCourse("CS101", "Intro to CS")
        dept.add_course(course)
        self.assertIn(course, dept.courses)

    def test_assign_student_to_department(self):
        dept = Department(1, self.conn)
        dept.assign_student_to_department(1001)
        self.cursor.execute("SELECT department_id FROM Student WHERE student_id=1001")
        dept_id = self.cursor.fetchone()[0]
        self.assertEqual(dept_id, 1)
        self.assertIn(1001, dept.students)

    def test_assign_student_multiple_times(self):
        dept = Department(1, self.conn)
        dept.assign_student_to_department(1001)
        dept.assign_student_to_department(1001)  # assigning again
        self.assertEqual(dept.students.count(1001), 1)  # should not duplicate

if __name__ == "__main__":
    unittest.main()
