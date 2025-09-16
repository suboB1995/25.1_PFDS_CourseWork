import sqlite3
import copy
from question1_university_system.person import Person

DB_FILE = "university_system.db"

# ------------------------------ Base Student ------------------------------
class Student(Person):
    """
    Base Student class that extends Person.
    """
    def __init__(self, person_id: int, name: str = None, db: sqlite3.Connection = None):
        """
        Initialize a Student object.

        Args:
            person_id (int): ID of the person in the Person table.
            name (str, optional): Student's name (overrides DB if provided).
            db (sqlite3.Connection, optional): Existing DB connection, or creates new if None.

        Raises:
            ValueError: If no matching student record is found in the database.
        """
        super().__init__(person_id, name, role="Student", db=db)
        self.db = db or sqlite3.connect(DB_FILE)

        # Load student details from the database
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT s.student_id, s.department_id, s.level, 
                   p.name, p.email, p.phone_number, p.dob
            FROM Student s
            JOIN Person p ON s.person_id = p.person_id
            WHERE s.person_id = ?
        """, (person_id,))
        result = cursor.fetchone()

        if result:
            (self.student_id,
             self.department_id,
             self.level,
             self.name,
             self.email,
             self.phone,
             self.dob) = result
        else:
            raise ValueError(f"No student found with person_id={person_id}")

    def get_responsibilities(self) -> str:
        """
        Get general responsibilities of any student.

        Returns:
            str: Description of responsibilities.
        """
        return f"{self.name}: Attend classes, complete assignments, and study."

# ------------------------------ SecureStudentRecord ------------------------------
class SecureStudentRecord(Student):
    """
    Adds secure academic record handling for a student.
    Handles enrollment, course management, GPA across semesters, and academic status.
    """

    MAX_COURSES = 2  # Limit to avoid overloading students

    def __init__(self, person_id: int, db: sqlite3.Connection = None):
        super().__init__(person_id, db=db)
        self.__courses = {}  # Private dict: {semester: {course_name: grade}}
        self.load_courses()

    # ---------------- Private attributes ----------------
    @property
    def courses(self) -> dict:
        """
        Get a read-only copy of all courses across semesters.

        Returns:
            dict: {semester: {course_name: grade}}
        """
        return copy.deepcopy(self.__courses)

    @courses.setter
    def courses(self, semester_courses: dict):
        """
        Set courses for a semester with GPA validation (0.0-4.0).

        Args:
            semester_courses (dict): {semester: {course_name: grade}}

        Raises:
            ValueError: If any GPA grade is outside 0.0–4.0.
        """
        for sem, grades in semester_courses.items():
            for course, gpa in grades.items():
                if gpa is not None and not (0.0 <= gpa <= 4.0):
                    raise ValueError(f"GPA for {course} in {sem} must be between 0.0 and 4.0")
        self.__courses = semester_courses

    def load_courses(self):
        """
        Load all enrolled courses and grades from the database,
        organized by semester.

        Returns:
            None
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT c.name, e.gpa_points, e.semester
            FROM Enrollment e
            JOIN Course c ON e.course_id = c.course_id
            WHERE e.student_id = ?
        """, (self.student_id,))
        result = cursor.fetchall()

        self.__courses = {}
        for course_name, grade, semester in result:
            if semester not in self.__courses:
                self.__courses[semester] = {}
            self.__courses[semester][course_name] = grade

    def enroll_course(self, course_id: int, semester: str = "Fall 2025") -> str:
        """
        Enroll the student in a new course after checking enrollment limit and prerequisites.

        Args:
            course_id (int): Course ID to enroll in.
            semester (str, optional): Semester for enrollment. Defaults to "Fall 2025".

        Returns:
            str: Success or error message suitable for GUI display.
        """
        cursor = self.db.cursor()

        # Check maximum courses for student
        if len(self.__courses) >= self.MAX_COURSES:
            return f"{self.name} cannot enroll in more than {self.MAX_COURSES} courses."

        # Fetch course details
        cursor.execute("""
                       SELECT name, enrollment_limit
                       FROM Course
                       WHERE course_id = ?
                       """, (course_id,))
        course = cursor.fetchone()
        if not course:
            return f"Course with ID {course_id} not found."

        course_name, enrollment_limit = course

        # Already enrolled check
        if course_name in self.__courses:
            return f"{self.name} is already enrolled in {course_name}."

        # Check enrollment limit for the semester
        cursor.execute("""
                       SELECT COUNT(*)
                       FROM Enrollment
                       WHERE course_id = ?
                         AND semester = ?
                       """, (course_id, semester))
        enrolled_count = cursor.fetchone()[0]

        if enrollment_limit is not None and enrolled_count >= enrollment_limit:
            return f"Cannot enroll: {course_name} has reached its enrollment limit ({enrollment_limit})."

        # Check prerequisites
        cursor.execute("""
                       SELECT prereq_course_id
                       FROM CoursePrerequisites
                       WHERE course_id = ?
                       """, (course_id,))
        prereq_courses = [row[0] for row in cursor.fetchall()]

        for prereq_id in prereq_courses:
            cursor.execute("""
                           SELECT gpa_points
                           FROM Enrollment
                           WHERE student_id = ?
                             AND course_id = ?
                             AND gpa_points IS NOT NULL
                           """, (self.student_id, prereq_id))
            prereq_grade = cursor.fetchone()
            if not prereq_grade or prereq_grade[0] < 2.0:  # Passing grade assumed 2.0
                cursor.execute("SELECT name FROM Course WHERE course_id = ?", (prereq_id,))
                prereq_name = cursor.fetchone()[0]
                return f"Cannot enroll: prerequisite {prereq_name} not completed or failed."

        # Enroll student
        cursor.execute("""
                       INSERT INTO Enrollment (student_id, course_id, semester)
                       VALUES (?, ?, ?)
                       """, (self.student_id, course_id, semester))
        self.db.commit()

        # Update in-memory courses
        if semester not in self.__courses:
            self.__courses[semester] = {}
        self.__courses[semester][course_name] = None

        return f"{self.name} successfully enrolled in {course_name} for {semester}."

    def drop_course(self, course_id: int, semester: str) -> str:
        """
        Drop an enrolled course for a specific semester.

        Args:
            course_id (int): Course ID to drop.
            semester (str): Semester to drop from.

        Returns:
            str: Success or error message for GUI display.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT name FROM Course WHERE course_id = ?", (course_id,))
        course = cursor.fetchone()

        if not course:
            return f"Course with ID {course_id} not found."

        course_name = course[0]

        # Check if student is enrolled in this course for the given semester
        cursor.execute("""
                       SELECT enrollment_id
                       FROM Enrollment
                       WHERE student_id = ?
                         AND course_id = ?
                         AND semester = ?
                       """, (self.student_id, course_id, semester))
        enrollment = cursor.fetchone()

        if not enrollment:
            return f"{self.name} is not enrolled in {course_name} for {semester}. Cannot drop."

        # Perform deletion
        cursor.execute("""
                       DELETE
                       FROM Enrollment
                       WHERE student_id = ?
                         AND course_id = ?
                         AND semester = ?
                       """, (self.student_id, course_id, semester))
        self.db.commit()

        # Update local cache (only if exists for that semester)
        if course_name in self.__courses:
            del self.__courses[course_name]

        return f"{self.name} has dropped {course_name} for {semester}."

    def view_grades(self) -> dict:
        """
        View current courses and grades.

        Returns:
            dict: Mapping of course_name -> grade.
        """
        return self.__courses.copy()

    def calculate_gpa(self) -> float:
        """
        Compute GPA across all semesters.

        Returns:
            float: Average GPA (0.0 if no grades).
        """
        all_grades = []
        for sem_courses in self.__courses.values():
            for grade in sem_courses.values():
                if grade is not None:
                    if not (0.0 <= grade <= 4.0):
                        raise ValueError(f"Invalid GPA {grade}. Must be 0.0–4.0.")
                    all_grades.append(grade)

        return sum(all_grades) / len(all_grades) if all_grades else 0.0

    def get_academic_status(self) -> str:
        """
        Determine academic status based on GPA.

        Returns:
            str: One of "Dean's List", "Probation", or "Good Standing".
        """
        gpa = self.calculate_gpa()
        if gpa >= 3.5:
            return "Dean's List"
        elif gpa < 2.0:
            return "Probation"
        else:
            return "Good Standing"

    def get_responsibilities(self) -> str:
        """
        Get student responsibilities with academic context.

        Returns:
            str: Responsibilities description.
        """
        return f"{self.name}: Attend classes, complete assignments, and study."


# ------------------------------ Utility Function ------------------------------
def ensure_column_exists(conn, table_name: str, column_name: str, column_def: str):
    """
    Ensure a column exists in the given table. Adds it if missing.

    Args:
        conn (sqlite3.Connection): Database connection.
        table_name (str): Table name to check.
        column_name (str): Column name to ensure.
        column_def (str): SQL column definition (e.g., "TEXT", "INTEGER").

    Returns:
        None
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [row[1] for row in cursor.fetchall()]
    if column_name not in cols:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
        conn.commit()


# ------------------------------ Undergraduate Student ------------------------------
class UndergraduateStudent(SecureStudentRecord):
    """Specialized student with a declared major."""

    def __init__(self, person_id: int, major: str, db: sqlite3.Connection = None):
        """
        Initialize an UndergraduateStudent.

        Args:
            person_id (int): Student's person ID.
            major (str): Declared major.
            db (sqlite3.Connection, optional): DB connection.
        """
        super().__init__(person_id, db=db)
        self.major = major

        ensure_column_exists(self.db, "Student", "major", "TEXT")
        cursor = self.db.cursor()
        cursor.execute("UPDATE Student SET major=? WHERE student_id=?", (self.major, self.student_id))
        self.db.commit()

    def get_responsibilities(self) -> str:
        """
        Get undergraduate responsibilities.

        Returns:
            str: Description of responsibilities.
        """
        return f"{self.name}: Undergraduate responsibilities include focusing on {self.major} courses."


# ------------------------------ Graduate Student ------------------------------
class GraduateStudent(SecureStudentRecord):
    """Specialized student with a thesis requirement."""

    def __init__(self, person_id: int, thesis_title: str, db: sqlite3.Connection = None):
        """
        Initialize a GraduateStudent.

        Args:
            person_id (int): Student's person ID.
            thesis_title (str): Title of thesis research.
            db (sqlite3.Connection, optional): DB connection.
        """
        super().__init__(person_id, db=db)
        self.thesis_title = thesis_title

        ensure_column_exists(self.db, "Student", "thesis_title", "TEXT")
        cursor = self.db.cursor()
        cursor.execute("UPDATE Student SET thesis_title=? WHERE student_id=?", (self.thesis_title, self.student_id))
        self.db.commit()

    def get_responsibilities(self) -> str:
        """
        Get graduate student responsibilities.

        Returns:
            str: Description of responsibilities.
        """
        return f"{self.name}: Graduate responsibilities include research and thesis work on '{self.thesis_title}'."
