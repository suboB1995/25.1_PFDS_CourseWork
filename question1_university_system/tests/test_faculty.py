import unittest
import sqlite3
from question1_university_system.faculty import Faculty, Professor, Lecturer, TeachingAssistant

class TestFaculty(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory database and sample data before each test"""
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # ------------------- Create Tables -------------------
        self.cursor.execute("""
        CREATE TABLE Person (
            person_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone_number TEXT,
            dob TEXT,
            role TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE Faculty (
            faculty_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            department_id INTEGER,
            FOREIGN KEY(person_id) REFERENCES Person(person_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE Course (
            course_id INTEGER PRIMARY KEY,
            name TEXT,
            faculty_id INTEGER,
            FOREIGN KEY(faculty_id) REFERENCES Faculty(faculty_id)
        )""")

        self.cursor.execute("""
        CREATE TABLE Enrollment (
            enrollment_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            course_id INTEGER,
            gpa_points REAL
        )""")

        self.cursor.execute("""
        CREATE TABLE Student (
            student_id    INTEGER PRIMARY KEY,
            person_id     INTEGER,
            department_id INTEGER,
            level         TEXT,
            major         TEXT,
            thesis_title  TEXT,
            supervisor_id INTEGER DEFAULT NULL
        )""")

        self.cursor.execute("""
        CREATE TABLE FacultyWorkload (
            workload_id    INTEGER PRIMARY KEY,
            faculty_id     INTEGER NOT NULL UNIQUE,
            teaching_hours INTEGER,
            research_hours INTEGER,
            support_hours  INTEGER,
            total_hours    INTEGER
        )""")

        # ------------------- Insert Sample Data -------------------
        # Insert a faculty person
        self.cursor.execute("INSERT INTO Person (person_id, name, role) VALUES (1, 'Dr. Namal', 'Faculty')")
        self.cursor.execute("INSERT INTO Faculty (faculty_id, person_id, department_id) VALUES (1, 1, 101)")

        # Insert courses
        self.cursor.execute("INSERT INTO Course (course_id, name, faculty_id) VALUES (1, 'Math 101', 1)")
        self.cursor.execute("INSERT INTO Course (course_id, name, faculty_id) VALUES (2, 'Physics 101', 1)")

        # Insert a student enrolled in Math 101
        self.cursor.execute("INSERT INTO Enrollment (enrollment_id, student_id, course_id, gpa_points) VALUES (1, 1001, 1, NULL)")

        # Insert a workload for Faculty
        self.cursor.execute("""
        INSERT INTO FacultyWorkload (workload_id, faculty_id, teaching_hours, research_hours, support_hours, total_hours)
        VALUES (1, 1, 5, 3, 2, 10)
        """)

        self.conn.commit()

        # ------------------- Create Faculty Object -------------------
        self.faculty = Faculty(person_id=1, db=self.conn)

    def tearDown(self):
        """Close DB after each test"""
        self.conn.close()

    # ------------------- Tests -------------------
    def test_assign_grade_valid(self):
        self.faculty.assign_grade(student_id=1001, course_id=1, grade=3.5)
        self.cursor.execute("SELECT gpa_points FROM Enrollment WHERE student_id=? AND course_id=?", (1001, 1))
        grade = self.cursor.fetchone()[0]
        self.assertEqual(grade, 3.5)

    def test_assign_grade_invalid(self):
        self.faculty.assign_grade(student_id=1001, course_id=1, grade=5.0)
        self.cursor.execute("SELECT gpa_points FROM Enrollment WHERE student_id=? AND course_id=?", (1001, 1))
        grade = self.cursor.fetchone()[0]
        self.assertIsNone(grade)

    def test_assign_grade_student_not_enrolled(self):
        self.faculty.assign_grade(student_id=2000, course_id=1, grade=3.0)
        self.cursor.execute("SELECT COUNT(*) FROM Enrollment WHERE student_id=2000 AND course_id=1")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)

    def test_calculate_workload(self):
        workload = self.faculty.calculate_workload()
        self.assertEqual(workload, 2)  # 2 courses

    def test_get_responsibilities(self):
        resp = self.faculty.get_responsibilities()
        self.assertIn("Teach", resp)
        self.assertIn("mentor students", resp)

    def test_professor_workload_and_responsibilities(self):
        # Insert a graduate student supervised by this professor
        self.cursor.execute("""
        INSERT INTO Student (student_id, person_id, department_id, level, thesis_title, supervisor_id)
        VALUES (2, 2, 101, 'Graduate', 'AI Research', 1)
        """)
        self.conn.commit()

        prof = Professor(person_id=1, db=self.conn)
        workload = prof.calculate_workload()
        self.assertEqual(workload, 3)  # 2 courses + 1 supervised student

        resp = prof.get_responsibilities()
        self.assertIn("supervise graduate students", resp)

    def test_lecturer_workload_and_responsibilities(self):
        lecturer = Lecturer(person_id=1, db=self.conn)
        workload = lecturer.calculate_workload()
        self.assertEqual(workload, 2)
        self.assertIn("Deliver 2 lectures", lecturer.get_responsibilities())

if __name__ == "__main__":
    unittest.main()
