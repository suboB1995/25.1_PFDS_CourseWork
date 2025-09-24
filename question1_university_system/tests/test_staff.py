import sqlite3
import unittest

from CourseWork.question1_university_system.staff import Staff


class TestStaff(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory database and tables before each test"""
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # ------------------- Create Tables -------------------
        self.cursor.execute("""
                            CREATE TABLE Person
                            (
                                person_id    INTEGER PRIMARY KEY,
                                name         TEXT,
                                email        TEXT,
                                phone_number TEXT,
                                role         TEXT,
                                dob          TEXT,
                                address      TEXT
                            )""")

        self.cursor.execute("""
                            CREATE TABLE Department
                            (
                                department_id INTEGER PRIMARY KEY,
                                name          TEXT
                            )""")

        self.cursor.execute("""
                            CREATE TABLE Staff
                            (
                                staff_id      INTEGER PRIMARY KEY,
                                person_id     INTEGER,
                                department_id INTEGER,
                                FOREIGN KEY (person_id) REFERENCES Person (person_id),
                                FOREIGN KEY (department_id) REFERENCES Department (department_id)
                            )""")

        # Insert a sample department
        self.cursor.execute("INSERT INTO Department (department_id, name) VALUES (1, 'Admin Department')")
        self.conn.commit()

    def tearDown(self):
        """Close DB after each test"""
        self.conn.close()

    # ------------------- Tests -------------------
    def test_create_new_staff_auto_insert(self):
        """Test creating a new Staff inserts into Person and Staff tables"""
        staff = Staff(name="Sunil", email="sunil@gmail.com", role="Admin", db=self.conn)

        # Person table should have new entry
        self.cursor.execute("SELECT name, role FROM Person WHERE person_id=?", (staff.person_id,))
        row = self.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Sunil")
        self.assertEqual(row[1], "Admin")

        # Staff table should have new entry
        self.cursor.execute("SELECT person_id, department_id FROM Staff WHERE staff_id=?", (staff.staff_id,))
        staff_row = self.cursor.fetchone()
        self.assertIsNotNone(staff_row)
        self.assertEqual(staff_row[0], staff.person_id)
        self.assertEqual(staff_row[1], 1)  # default department

    def test_create_existing_staff_load_details(self):
        """Test loading existing staff fetches staff_id and department_id"""
        # First, insert manually
        self.cursor.execute("""
                            INSERT INTO Person (person_id, name, email, role)
                            VALUES (10, 'Kamala', 'kamala@gmail.com', 'Admin')
                            """)
        self.cursor.execute("INSERT INTO Staff (staff_id, person_id, department_id) VALUES (5, 10, 1)")
        self.conn.commit()

        # Create Staff object with existing person_id
        staff = Staff(person_id=10, db=self.conn)
        self.assertEqual(staff.staff_id, 5)
        self.assertEqual(staff.department_id, 1)

    def test_insert_person_returns_id(self):
        """Test insert_person returns a valid new person_id"""
        staff = Staff(name="Geetha", db=self.conn)
        person_id = staff.insert_person()
        self.assertIsInstance(person_id, int)
        self.cursor.execute("SELECT name FROM Person WHERE person_id=?", (person_id,))
        self.assertEqual(self.cursor.fetchone()[0], "Geetha")

    def test_insert_staff_returns_id_and_assigns_department(self):
        """Test insert_staff returns staff_id and assigns default department"""
        staff = Staff(name="Mala", db=self.conn)
        staff_id = staff.insert_staff()
        self.assertIsInstance(staff_id, int)
        self.cursor.execute("SELECT department_id FROM Staff WHERE staff_id=?", (staff_id,))
        dept_id = self.cursor.fetchone()[0]
        self.assertEqual(dept_id, 1)  # default department

    def test_get_responsibilities(self):
        """Test get_responsibilities returns correct string"""
        staff = Staff(name="Sugath", db=self.conn)
        resp = staff.get_responsibilities()
        self.assertIn("Sugath", resp)
        self.assertIn("Manage administrative tasks", resp)


if __name__ == "__main__":
    unittest.main()
