import sqlite3
import unittest

from CourseWork.question1_university_system.student import UndergraduateStudent, GraduateStudent, SecureStudentRecord


# --------------------------- Test Setup ---------------------------

class TestStudentRecords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create in-memory DB and populate tables with sample data."""
        cls.conn = sqlite3.connect(":memory:")
        cursor = cls.conn.cursor()

        # Create Person table
        cursor.execute("""
                       CREATE TABLE Person
                       (
                           person_id    INTEGER PRIMARY KEY,
                           name         TEXT,
                           email        TEXT,
                           phone_number TEXT,
                           dob          TEXT
                       )
                       """)

        # Create Student table
        cursor.execute("""
                       CREATE TABLE Student
                       (
                           student_id    INTEGER PRIMARY KEY,
                           person_id     INTEGER,
                           department_id INTEGER,
                           level         TEXT,
                           major         TEXT,
                           thesis_title  TEXT
                       )
                       """)

        # Create Course table
        cursor.execute("""
                       CREATE TABLE Course
                       (
                           course_id        INTEGER PRIMARY KEY,
                           department_id    INTEGER,
                           name             TEXT,
                           credits          INTEGER,
                           enrollment_limit INTEGER,
                           faculty_id       INTEGER
                       )
                       """)

        # Create Enrollment table
        cursor.execute("""
                       CREATE TABLE Enrollment
                       (
                           enrollment_id INTEGER PRIMARY KEY,
                           student_id    INTEGER,
                           course_id     INTEGER,
                           semester      TEXT,
                           grade         TEXT,
                           gpa_points    REAL
                       )
                       """)

        # Create CoursePrerequisites table
        cursor.execute("""
                       CREATE TABLE CoursePrerequisites
                       (
                           id               INTEGER PRIMARY KEY,
                           course_id        INTEGER,
                           prereq_course_id INTEGER
                       )
                       """)

        # Insert sample Person and Student
        cursor.execute("INSERT INTO Person (person_id, name) VALUES (1, 'Nayana')")
        cursor.execute("INSERT INTO Student (student_id, person_id, department_id, level) VALUES (1, 1, 101, 'UG')")

        # Insert sample Courses
        cursor.execute("INSERT INTO Course (course_id, name, enrollment_limit) VALUES (101, 'Intro to CS', 2)")
        cursor.execute("INSERT INTO Course (course_id, name, enrollment_limit) VALUES (102, 'Data Structures', 2)")

        # Insert a prerequisite: Data Structures requires Intro to CS
        cursor.execute("INSERT INTO CoursePrerequisites (course_id, prereq_course_id) VALUES (102, 101)")

        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # -------------------- Test Cases --------------------

    def test_undergraduate_initialization(self):
        student = UndergraduateStudent(person_id=1, major="CS", db=self.conn)
        self.assertEqual(student.name, "Nayana")
        self.assertEqual(student.major, "CS")
        self.assertIsInstance(student, SecureStudentRecord)

    def test_graduate_initialization(self):
        # Add a graduate student record
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO Student (student_id, person_id, department_id, level, thesis_title) VALUES (2, 1, 101, 'GR', 'AI Research')")
        self.conn.commit()

        student = GraduateStudent(person_id=1, thesis_title="AI Research", db=self.conn)
        self.assertEqual(student.thesis_title, "AI Research")
        self.assertIsInstance(student, SecureStudentRecord)

    def test_enroll_course_success(self):
        student = UndergraduateStudent(person_id=1, major="CS", db=self.conn)
        msg = student.enroll_course(101, "Fall 2025")
        self.assertIn("successfully enrolled", msg.lower())

    def test_enroll_course_prerequisite_fail(self):
        student = UndergraduateStudent(person_id=1, major="CS", db=self.conn)
        # Try to enroll in Data Structures without completing Intro to CS
        msg = student.enroll_course(102, "Fall 2025")
        self.assertIn("prerequisite", msg.lower())

    def test_drop_course_success(self):
        student = UndergraduateStudent(person_id=1, major="CS", db=self.conn)
        student.enroll_course(101, "Fall 2025")
        msg = student.drop_course(101, "Fall 2025")
        self.assertIn("dropped", msg.lower())

    def test_drop_course_not_enrolled(self):
        student = UndergraduateStudent(person_id=1, major="CS", db=self.conn)
        msg = student.drop_course(101, "Fall 2025")
        self.assertIn("nayana has dropped intro to cs for fall 2025.", msg.lower())

    def test_calculate_gpa(self):
        student = UndergraduateStudent(person_id=1, major="CS", db=self.conn)
        # Enroll in a course with grades
        student.enroll_course(101, "Fall 2025")
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Enrollment SET gpa_points=? WHERE student_id=? AND course_id=?",
                       (3.5, student.student_id, 101))
        self.conn.commit()
        student.load_courses()  # Refresh in-memory data
        gpa = student.calculate_gpa()
        self.assertEqual(gpa, 3.5)

    def test_academic_status_deans_list(self):
        student = UndergraduateStudent(person_id=1, major="CS", db=self.conn)
        student.enroll_course(101, "Fall 2025")
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Enrollment SET gpa_points=? WHERE student_id=? AND course_id=?",
                       (3.8, student.student_id, 101))
        self.conn.commit()
        student.load_courses()
        status = student.get_academic_status()
        self.assertEqual(status, "Dean's List")

    def test_academic_status_probation(self):
        student = UndergraduateStudent(person_id=1, major="CS", db=self.conn)
        student.enroll_course(101, "Fall 2025")
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Enrollment SET gpa_points=? WHERE student_id=? AND course_id=?",
                       (1.5, student.student_id, 101))
        self.conn.commit()
        student.load_courses()
        status = student.get_academic_status()
        self.assertEqual(status, "Probation")


# --------------------------- Run Tests ---------------------------
if __name__ == "__main__":
    unittest.main()
