import sqlite3

import PySimpleGUI as sg

from faculty import Professor, Lecturer, TeachingAssistant

# ----------------- Database Connection -----------------
db_file = "university_system.db"
conn = sqlite3.connect(db_file)
conn.execute("PRAGMA foreign_keys = ON;")  # Ensure foreign key constraints are enforced


# ----------------- Helper function to create aligned input rows -----------------
def aligned_row(label_text, key, input_size=(30, 1)):
    """
    Create a row with a right-aligned label and an input field.

    Args:
        label_text (str): Label to display.
        key (str): Element key for retrieving input values.
        input_size (tuple): Size of the input field.

    Returns:
        list: Row layout for PySimpleGUI.
    """
    return [sg.Text(label_text, size=(15, 1), justification='right'),
            sg.Input(key=key, size=input_size)]


# ----------------- GUI Layout -----------------
layout = [
    [sg.Text("University Faculty Management",
             font=("Arial", 16), justification="center", expand_x=True)],

    # ---- Section: Find Faculty ----
    [sg.Frame(layout=[
        [sg.Text("Faculty Type:", size=(15, 1), justification="right"),
         sg.Combo(["Professor", "Lecturer", "Teaching Assistant"],
                  key="-FACULTY_TYPE-", readonly=True, size=(28, 1))],
        aligned_row("Person ID:", "-PERSON_ID-"),
        [sg.Push(), sg.Button("Find Faculty")]
    ], title="Find Faculty", expand_x=True)],

    # ---- Section: Faculty Information ----
    [sg.Frame(layout=[
        [sg.Multiline("", size=(60, 6), key="-INFO-", disabled=True)]
    ], title="Faculty Information", expand_x=True)],

    # ---- Section: Update Workload ----
    [sg.Frame(layout=[
        aligned_row("Teaching Hours:", "-TEACH_H-"),
        aligned_row("Research Hours:", "-RES_H-"),
        aligned_row("Support Hours:", "-SUP_H-"),
        [sg.Push(), sg.Button("Save Workload")]
    ], title="Update Workload", expand_x=True)],

    # ---- Section: Assign Grade ----
    [sg.Frame(layout=[
        aligned_row("Student ID:", "-STUDENT_ID-"),
        aligned_row("Course ID:", "-COURSE_ID-"),
        aligned_row("Grade (0.0 - 4.0):", "-GRADE-"),
        [sg.Push(), sg.Button("Assign Grade")]
    ], title="Assign Grade", expand_x=True)],

    [sg.Button("Exit")]
]

# ----------------- Create Window -----------------
window = sg.Window("University Faculty Management", layout, element_justification="center")

faculty_obj = None  # Placeholder for the currently loaded faculty object

# ----------------- Event Loop -----------------
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break  # Exit application

    try:
        # -------- Find Faculty --------
        if event == "Find Faculty":
            pid = int(values["-PERSON_ID-"])
            ftype = values["-FACULTY_TYPE-"]

            # Instantiate the correct faculty type
            if ftype == "Professor":
                faculty_obj = Professor(pid, db=conn)
            elif ftype == "Lecturer":
                faculty_obj = Lecturer(pid, db=conn)
            elif ftype == "Teaching Assistant":
                faculty_obj = TeachingAssistant(pid, db=conn)
            else:
                sg.popup_error("Select a valid faculty type")
                continue

            # Fetch workload information from DB
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT teaching_hours, research_hours, support_hours, total_hours
                           FROM FacultyWorkload
                           WHERE faculty_id = ?
                           """, (faculty_obj.faculty_id,))
            workload = cursor.fetchone()
            teach, research, support, total = workload if workload else (0, 0, 0, 0)

            # Display faculty info + workload
            info_text = f"""Loaded {ftype}:
            Name: {faculty_obj.name}
            Faculty ID: {faculty_obj.faculty_id}

            Current Workload:
              • Teaching: {teach}
              • Research: {research}
              • Support: {support}
              • Total: {total}"""
            window["-INFO-"].update(info_text)

            # Prefill workload input fields
            window["-TEACH_H-"].update(str(teach))
            window["-RES_H-"].update(str(research))
            window["-SUP_H-"].update(str(support))

        # -------- Save Workload --------
        elif event == "Save Workload":
            if faculty_obj:
                try:
                    # Get values from inputs (default to 0 if empty)
                    teach = int(values["-TEACH_H-"] or 0)
                    research = int(values["-RES_H-"] or 0)
                    support = int(values["-SUP_H-"] or 0)

                    # Save workload via Faculty class
                    faculty_obj.save_workload(teach, research, support)
                    sg.popup("Success",
                             f"Workload saved successfully! Total hours: {teach + research + support}")
                except ValueError:
                    sg.popup_error("Please enter valid integer numbers for workload hours.")
            else:
                sg.popup_error("Find a faculty first.")

        # -------- Assign Grade --------
        elif event == "Assign Grade":
            if faculty_obj:
                try:
                    # Get values from inputs
                    student_id = int(values["-STUDENT_ID-"])
                    course_id = int(values["-COURSE_ID-"])
                    raw_grade = values["-GRADE-"]

                    # Validate grade
                    try:
                        grade = float(raw_grade)
                        if not (0.0 <= grade <= 4.0):
                            raise ValueError
                    except Exception:
                        sg.popup_error(f"Grade must be between 0.0 and 4.0. You entered: {raw_grade}")
                        continue  # Stop processing further

                    # Assign grade via Faculty class
                    faculty_obj.assign_grade(student_id, course_id, grade)
                    sg.popup("Success",
                             f"Grade {grade} assigned to Student {student_id} for Course {course_id}")
                except ValueError:
                    sg.popup_error("Please enter valid numbers.")
                except Exception as e:
                    sg.popup_error(f"Unexpected Error: {e}")
            else:
                sg.popup_error("Find a faculty first.")

    except Exception as e:
        sg.popup_error(f"Error: {e}")

# ----------------- Close DB and Window -----------------
conn.close()
window.close()
