import sqlite3

DB_FILE = "university_system.db"

class Person:
    """
    Base class representing a person in the university system.
    Attributes match the Person table in the database.
    """

    def __init__(self, person_id: int, name: str, email: str = None,
                 phone_number: str = None, role: str = None,
                 dob: str = None, address: str = None,
                 db: sqlite3.Connection = None):
        """
        Initialize a person with DB-related attributes.
        :param person_id: Unique ID from the database
        :param name: Full name of the person
        :param email: Email address
        :param phone_number: Contact number
        :param role: Role (Student, Faculty, Staff, Admin, etc.)
        :param dob: Date of birth (YYYY-MM-DD)
        :param address: Residential address
        :param db: sqlite3 connection (optional)
        """
        self.person_id = person_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.role = role
        self.dob = dob
        self.address = address

        # Ensure we always have a DB connection
        self.db = db or sqlite3.connect(DB_FILE)

    def load_from_db(self):
        """
        Load the latest person details from the DB into this instance.
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT name, email, phone_number, role, dob, address
            FROM Person
            WHERE person_id = ?
        """, (self.person_id,))
        row = cursor.fetchone()
        if row:
            self.name, self.email, self.phone_number, self.role, self.dob, self.address = row
        else:
            raise ValueError(f"Person with ID {self.person_id} not found in DB.")

    def get_responsibilities(self) -> str:
        """
        Base method for responsibilities.
        Can be overridden by subclasses (Student, Faculty, Staff, etc.).
        """
        return f"{self.name}: General responsibilities for a person."
