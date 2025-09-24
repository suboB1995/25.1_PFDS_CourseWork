import sqlite3

from CourseWork.question1_university_system.person import Person


class Staff(Person):
    """
    Staff member in the university system.
    Inherits from Person and can:
    - Assign students to departments
    - Assign faculty to courses
    - Manage administrative tasks
    """

    def __init__(self, person_id: int = None, name: str = None, email: str = None,
                 phone_number: str = None, role: str = "Admin", dob: str = None,
                 address: str = None, department_id: int = None,
                 db: sqlite3.Connection = None):
        """
        Initialize a Staff object.

        Args:
            person_id (int, optional): ID of the staff in the Person table (if existing).
            name (str, optional): Name of the staff member.
            email (str, optional): Email address.
            phone_number (str, optional): Phone number.
            role (str, optional): Role (default = "Admin").
            dob (str, optional): Date of birth.
            address (str, optional): Address of staff.
            department_id (int, optional): Department assigned.
            db (sqlite3.Connection, optional): Database connection.

        Returns:
            None
        """
        super().__init__(person_id=person_id, name=name, email=email,
                         phone_number=phone_number, role=role,
                         dob=dob, address=address)
        self.db = db
        self.department_id = department_id
        self.staff_id = None

        if self.db:
            if self.person_id is None:
                # Brand new staff → insert
                self.person_id = self.insert_person()
                self.staff_id = self.insert_staff()
            else:
                # Existing staff → fetch department and staff_id
                self.load_staff_details()

    def insert_person(self) -> int:
        """
        Insert the staff into the Person table.

        Args:
            None

        Returns:
            int: The newly created person_id for the staff.
        """
        cursor = self.db.cursor()
        cursor.execute("""
                       INSERT INTO Person (name, email, phone_number, role, dob, address)
                       VALUES (?, ?, ?, ?, ?, ?)
                       """, (self.name, self.email, self.phone_number,
                             self.role, self.dob, self.address))
        self.db.commit()
        return cursor.lastrowid

    def insert_staff(self) -> int:
        """
        Insert staff into the Staff table with department assignment.

        Args:
            None

        Returns:
            int: The newly created staff_id.
        """
        cursor = self.db.cursor()
        if self.department_id is None:
            # Assign to a default department if not specified
            cursor.execute("SELECT department_id FROM Department LIMIT 1;")
            row = cursor.fetchone()
            self.department_id = row[0] if row else 1

        cursor.execute("""
                       INSERT INTO Staff (person_id, department_id)
                       VALUES (?, ?)
                       """, (self.person_id, self.department_id))
        self.db.commit()
        return cursor.lastrowid

    def load_staff_details(self) -> None:
        """
        Load existing staff details from the database.

        Args:
            None

        Returns:
            None
        """
        cursor = self.db.cursor()
        cursor.execute("""
                       SELECT staff_id, department_id
                       FROM Staff
                       WHERE person_id = ?
                       """, (self.person_id,))
        row = cursor.fetchone()
        if row:
            self.staff_id, self.department_id = row

    def get_responsibilities(self) -> str:
        """
        Get staff responsibilities.

        Args:
            None

        Returns:
            str: Responsibilities of the staff member.
        """
        return f"{self.name}: Manage administrative tasks and support faculty and students."
