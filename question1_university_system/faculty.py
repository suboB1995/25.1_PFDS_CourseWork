import sqlite3

from CourseWork.question1_university_system.person import Person

DB_FILE = "university_system.db"


# ------------------------------ Base Faculty ------------------------------
class Faculty(Person):
    """
    Base Faculty class that extends Person.
    Provides functionality common to all faculty members
    such as assigning grades, managing workload, and responsibilities.
    """

    def __init__(self, person_id: int, name: str = None, db: sqlite3.Connection = None):
        """
        Initialize a Faculty object.

        Args:
            person_id (int): Person ID associated with this faculty member.
            name (str, optional): Faculty name. Defaults to None.
            db (sqlite3.Connection, optional): Database connection. If not provided, a new connection is created.

        Raises:
            ValueError: If no faculty record is found for the given person_id.
        """
        super().__init__(person_id, name, role="Faculty", db=db)
        self.db = db or sqlite3.connect(DB_FILE)

        # Fetch faculty information from DB
        cursor = self.db.cursor()
        cursor.execute("""
                       SELECT f.faculty_id, f.department_id, p.name, p.email, p.phone_number, p.dob
                       FROM Faculty f
                                JOIN Person p ON f.person_id = p.person_id
                       WHERE f.person_id = ?
                       """, (person_id,))
        result = cursor.fetchone()

        if result:
            self.faculty_id, self.department_id, self.name, self.email, self.phone, self.dob = result
        else:
            raise ValueError(f"No faculty found with person_id={person_id}")

    # ----------------------------------------------------------------------
    def assign_grade(self, student_id: int, course_id: int, grade: float):
        """
        Assign a grade to a student for a specific course.

        Args:
            student_id (int): Student ID.
            course_id (int): Course ID.
            grade (float): GPA points (between 0.0 and 4.0).

        Returns:
            None
        """
        # Validate grade range
        if not (0.0 <= grade <= 4.0):
            print(f"Invalid grade {grade}. Must be between 0.0 and 4.0")
            return

        cursor = self.db.cursor()

        # Ensure student is enrolled in the course
        cursor.execute("""
                       SELECT 1
                       FROM Enrollment
                       WHERE student_id = ?
                         AND course_id = ?
                       """, (student_id, course_id))
        if not cursor.fetchone():
            print(f"Student {student_id} is not enrolled in course {course_id}")
            return

        # Update grade
        cursor.execute("""
                       UPDATE Enrollment
                       SET gpa_points = ?
                       WHERE student_id = ?
                         AND course_id = ?
                       """, (grade, student_id, course_id))
        self.db.commit()

        print(f"Grade {grade} assigned to Student {student_id} for Course {course_id}")

    # ----------------------------------------------------------------------
    def calculate_workload(self) -> int:
        """
        Default workload calculation.
        For base Faculty, workload = number of courses taught.

        Returns:
            int: Number of courses taught.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM Course WHERE faculty_id = ?", (self.faculty_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    # ----------------------------------------------------------------------
    def save_workload(self, teaching_hours: int, research_hours: int, support_hours: int):
        """
        Save or update workload details for the faculty in the FacultyWorkload table.

        Args:
            teaching_hours (int): Hours spent teaching.
            research_hours (int): Hours spent on research.
            support_hours (int): Hours spent on academic support.

        Returns:
            None
        """
        total_hours = teaching_hours + research_hours + support_hours
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Insert or update workload
        cursor.execute("""
                       INSERT INTO FacultyWorkload (faculty_id, teaching_hours, research_hours, support_hours,
                                                    total_hours)
                       VALUES (?, ?, ?, ?, ?) ON CONFLICT(faculty_id) DO
                       UPDATE SET
                           teaching_hours=excluded.teaching_hours,
                           research_hours=excluded.research_hours,
                           support_hours=excluded.support_hours,
                           total_hours=excluded.total_hours
                       """, (self.faculty_id, teaching_hours, research_hours, support_hours, total_hours))

        conn.commit()
        conn.close()
        print(f"Workload saved: Total {total_hours} hours")

    # ----------------------------------------------------------------------
    def get_responsibilities(self) -> str:
        """
        Get default responsibilities of a faculty member.

        Returns:
            str: Description of responsibilities.
        """
        workload = self.calculate_workload()
        return f"{self.name}: Teach {workload} course(s), mentor students, prepare lectures, evaluate students."


# ------------------------------ Specialized Faculty ------------------------------
class Professor(Faculty):
    """
    Professor class.
    Professors have additional responsibility of supervising graduate students.
    """

    def calculate_workload(self) -> int:
        """
        Workload for professors = number of courses taught + number of graduate students supervised.

        Returns:
            int: Combined workload.
        """
        cursor = self.db.cursor()

        # Count courses taught
        cursor.execute("SELECT COUNT(*) FROM Course WHERE faculty_id = ?", (self.faculty_id,))
        courses = cursor.fetchone()[0] or 0

        # Count supervised graduate students
        cursor.execute("SELECT COUNT(*) FROM Student WHERE supervisor_id = ? AND level='Graduate'", (self.faculty_id,))
        grad_students = cursor.fetchone()[0] or 0

        return courses + grad_students

    def get_responsibilities(self) -> str:
        """
        Get responsibilities of a professor.

        Returns:
            str: Description of professor responsibilities.
        """
        workload = self.calculate_workload()
        return f"{self.name}: Teach {workload} course(s) and supervise graduate students."


class Lecturer(Faculty):
    """
    Lecturer class.
    Lecturers mainly focus on delivering lectures and grading assignments.
    """

    def calculate_workload(self) -> int:
        """
        Workload for lecturers = number of courses taught.

        Returns:
            int: Number of courses taught.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM Course WHERE faculty_id = ?", (self.faculty_id,))
        return cursor.fetchone()[0] or 0

    def get_responsibilities(self) -> str:
        """
        Get responsibilities of a lecturer.

        Returns:
            str: Description of lecturer responsibilities.
        """
        workload = self.calculate_workload()
        return f"{self.name}: Deliver {workload} lectures and grade assignments."


class TeachingAssistant(Faculty):
    """
    Teaching Assistant (TA) class.
    TAs usually support faculty with labs, tutorials, and grading.
    """

    def calculate_workload(self) -> int:
        """
        Workload for TAs = total hours from FacultyWorkload table.

        Returns:
            int: Total workload hours.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT total_hours FROM FacultyWorkload WHERE faculty_id = ?", (self.faculty_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_responsibilities(self) -> str:
        """
        Get responsibilities of a Teaching Assistant.

        Returns:
            str: Description of Teaching Assistant responsibilities.
        """
        workload = self.calculate_workload()
        if workload == 0:
            return f"{self.name}: No workload assigned yet."
        return f"{self.name}: Assist in labs/tutorials and grade exercises ({workload} hours)."
