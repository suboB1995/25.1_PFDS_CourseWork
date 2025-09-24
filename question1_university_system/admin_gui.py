import sqlite3

import PySimpleGUI as sg

from person import Person
from CourseWork.question1_university_system.course import Course
from CourseWork.question1_university_system.department import Department
from CourseWork.question1_university_system.faculty import Faculty, Professor, Lecturer, TeachingAssistant
from CourseWork.question1_university_system.student import Student, UndergraduateStudent, GraduateStudent
from staff import Staff

# ----------------- Database Connection -----------------
db_file = "university_system.db"
conn = sqlite3.connect(db_file)
conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key constraints

# ----------------- Create a Staff instance (Admin user for managing assignments) -----------------
staff_member = Staff(name="Admin Staff", db=conn)


# ----------------- Helper function to create aligned input rows -----------------
def aligned_row(label_text, key, input_size=(10, 1)):
    """
    Create a GUI row with a right-aligned label and an input field.

    Args:
        label_text (str): The label text to display.
        key (str): The unique key for the input field.
        input_size (tuple): Size of the input field (width, height).

    Returns:
        list: A list containing PySimpleGUI elements for one row.
    """
    return [sg.Text(label_text, size=(15, 1), justification='right'),
            sg.Input(key=key, size=input_size)]


# ----------------- GUI Layout -----------------
layout = [
    [sg.Text("University Staff Management", font=("Arial", 16),
             justification="center", expand_x=True)],

    # ---- Section: Student Assignment ---
    [sg.Frame(layout=[
        aligned_row("Student ID:", "-STUDENT_ID-", input_size=(30, 1)),
        aligned_row("Department ID:", "-DEPARTMENT_ID-", input_size=(30, 1)),
        [sg.Push(), sg.Button("Assign Student")]
    ], title="Assign Student to Department", expand_x=True)],

    # ---- Section: Faculty Assignment ---
    [sg.Frame(layout=[
        aligned_row("Faculty ID:", "-FACULTY_ID-", input_size=(30, 1)),
        aligned_row("Course ID:", "-COURSE_ID-", input_size=(30, 1)),
        [sg.Push(), sg.Button("Assign Faculty")]
    ], title="Assign Faculty to Course", expand_x=True)],

    # ---- Section: Check Responsibilities ---
    [sg.Frame(layout=[
        aligned_row("Person ID:", "-PERSON_ID-", input_size=(30, 1)),
        [sg.Push(), sg.Button("Check Responsibilities")],
        [sg.Multiline(size=(60, 5), key="-RESPONSIBILITIES-", disabled=True)]
    ], title="Check Responsibilities", expand_x=True)],

    [sg.Button("Exit")]
]

# ----------------- Create Window -----------------
window = sg.Window("University Staff Management", layout, element_justification="center")

# ----------------- Event Loop -----------------
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break

    # -------- Assign Student to Department --------
    if event == "Assign Student":
        try:
            student_id = int(values["-STUDENT_ID-"])
            department_id = int(values["-DEPARTMENT_ID-"])
            # Create or fetch the Department instance
            dept_obj = Department(department_id=department_id, db=conn)
            dept_obj.assign_student_to_department(student_id)
            sg.popup("Success", f"Student {student_id} assigned to Department {department_id}.")
        except Exception as e:
            sg.popup("Error", str(e))

    # -------- Assign Faculty to Course --------
    if event == "Assign Faculty":
        try:
            faculty_id = int(values["-FACULTY_ID-"])
            course_id = int(values["-COURSE_ID-"])
            course_obj = Course(course_id=course_id, db=conn)
            course_obj.assign_faculty_to_course(faculty_id)
            sg.popup("Success", f"Faculty {faculty_id} assigned to Course {course_id}.")
        except Exception as e:
            sg.popup("Error", str(e))

    # -------- Check Responsibilities of any Person (Student/Faculty/Admin/etc.) --------
    if event == "Check Responsibilities":
        try:
            person_id = int(values["-PERSON_ID-"])
            cursor = conn.cursor()

            # Get role + name from Person table
            cursor.execute("SELECT role, name FROM Person WHERE person_id = ?", (person_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Person ID {person_id} not found.")

            role, name = row

            # --- Student Case ---
            if role == "Student":
                cursor.execute("""
                               SELECT level, major, thesis_title
                               FROM Student
                               WHERE person_id = ?
                               """, (person_id,))
                srow = cursor.fetchone()
                if not srow:
                    raise ValueError(f"No student record for person_id={person_id}")

                level, major, thesis_title = srow

                if level == "Undergraduate":
                    person_obj = UndergraduateStudent(person_id=person_id, major=major or "General")
                elif level == "Graduate":
                    person_obj = GraduateStudent(person_id=person_id, thesis_title=thesis_title or "Untitled Thesis")
                else:
                    # Fallback to generic student
                    person_obj = Student(person_id=person_id, name=name, db=conn)

            # --- Faculty Case ---
            elif role == "Faculty":
                cursor.execute("SELECT type FROM Faculty WHERE person_id = ?", (person_id,))
                frow = cursor.fetchone()
                if not frow:
                    raise ValueError(f"No Faculty record for person_id={person_id}")

                faculty_type = frow[0]
                if faculty_type == "Professor":
                    person_obj = Professor(person_id=person_id, name=name, db=conn)
                elif faculty_type == "Lecturer":
                    person_obj = Lecturer(person_id=person_id, name=name, db=conn)
                elif faculty_type == "Teaching Assistant":
                    person_obj = TeachingAssistant(person_id=person_id, name=name, db=conn)
                else:
                    person_obj = Faculty(person_id=person_id, name=name, db=conn)

            # --- Admin Case ---
            elif role == "Admin":
                person_obj = Staff(person_id=person_id, name=name, db=conn)

            # --- Generic Person Fallback ---
            else:
                person_obj = Person(person_id=person_id, name=name, role=role, db=conn)

            # Get and display responsibilities
            responsibilities = person_obj.get_responsibilities()
            window["-RESPONSIBILITIES-"].update(responsibilities)

        except Exception as e:
            sg.popup("Error", str(e))

# ----------------- Close DB and Window -----------------
conn.close()
window.close()
