import sqlite3
import unittest

from CourseWork.question1_university_system.person import Person


class TestPerson(unittest.TestCase):

    def setUp(self):
        """Set up in-memory DB and sample data before each test"""
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # Create Person table
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

        # Insert sample person
        self.cursor.execute("""
                            INSERT INTO Person (person_id, name, email, phone_number, role, dob, address)
                            VALUES (1, 'Nimal Perera', 'nimal@gmail.com', '1234567890', 'Student', '2000-01-01',
                                    '123 Main Street, Kegalle')
                            """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_initialization(self):
        """Test creating a Person instance directly"""
        person = Person(person_id=1, name='Nimal Perera', db=self.conn)
        self.assertEqual(person.person_id, 1)
        self.assertEqual(person.name, 'Nimal Perera')
        self.assertEqual(person.db, self.conn)

    def test_load_from_db(self):
        """Test loading person data from database"""
        person = Person(person_id=1, name='Temp', db=self.conn)
        person.load_from_db()
        self.assertEqual(person.name, 'Nimal Perera')
        self.assertEqual(person.email, 'nimal@gmail.com')
        self.assertEqual(person.phone_number, '1234567890')
        self.assertEqual(person.role, 'Student')
        self.assertEqual(person.dob, '2000-01-01')
        self.assertEqual(person.address, '123 Main Street, Kegalle')

    def test_load_from_db_not_found(self):
        """Test loading a person ID that does not exist"""
        person = Person(person_id=999, name='Unknown', db=self.conn)
        with self.assertRaises(ValueError):
            person.load_from_db()

    def test_get_responsibilities(self):
        """Test base get_responsibilities method"""
        person = Person(person_id=1, name='Nimal Perera', db=self.conn)
        resp = person.get_responsibilities()
        self.assertIn('Nimal Perera', resp)
        self.assertIn('General responsibilities', resp)


if __name__ == "__main__":
    unittest.main()
