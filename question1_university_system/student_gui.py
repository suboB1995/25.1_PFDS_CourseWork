import datetime

import PySimpleGUI as sg

from student import UndergraduateStudent, GraduateStudent


# ----------------- Helper function to create aligned input rows -----------------
def aligned_row(label_text, key, input_size=(30, 1)):
    """
    Creates a row with a right-aligned label and input field for consistency.

    Args:
        label_text (str): The label displayed to the left of the input field.
        key (str): The unique key used to reference the input field.
        input_size (tuple): The width and height of the input field.

    Returns:
        list: A list containing a label and input element for use in the layout.
    """
    return [sg.Text(label_text, size=(15, 1), justification='right'),
            sg.Input(key=key, size=input_size)]


def generate_semesters(num_years: int = 2):
    """
    Generate semester options dynamically.
    Example: ["Fall 2025", "Spring 2026", "Summer 2026", ...]
    """
    current_year = datetime.datetime.now().year
    semesters = []
    for year in range(current_year, current_year + num_years):
        semesters.append(f"Fall {year}")
        semesters.append(f"Spring {year + 1}")
        semesters.append(f"Summer {year + 1}")
    return semesters


semester_options = generate_semesters(3)

# ----------------- GUI Layout -----------------
layout = [
    [sg.Text("University Student Management", font=("Arial", 16),
             justification="center", expand_x=True)],

    # ---- Section: Find Student ----
    [sg.Frame(layout=[
        [sg.Text("Student Type:", size=(15, 1), justification="right"),
         sg.Combo(["Undergraduate", "Graduate"], key="-STUDENT_TYPE-",
                  readonly=True, size=(28, 1))],
        aligned_row("Person ID:", "-PERSON_ID-"),
        aligned_row("Major / Thesis:", "-MAJOR_THESIS-"),
        [sg.Push(), sg.Button("Find Student")]
    ], title="Find Student", expand_x=True)],

    # ---- Section: Student Information ----
    [sg.Frame(layout=[
        [sg.Multiline("", size=(60, 10), key="-INFO-", disabled=True)]
    ], title="Student Information", expand_x=True)],

    # ---- Section: Course Management ----
    [sg.Frame(layout=[
        aligned_row("Course ID:", "-COURSE_ID-"),
        [sg.Text("Semester:", size=(15, 1), justification="right"),
         sg.Combo(
             semester_options,
             default_value=semester_options[0],  # Default to first option
             key="-SEMESTER-",
             readonly=True,
             size=(20, 1)
         )],
        [sg.Push(), sg.Button("Enroll Course"), sg.Button("Drop Course")]
    ], title="Course Management", expand_x=True)],

    # ---- Section: Academic Status ----
    [sg.Frame(layout=[
        [sg.Push(), sg.Button("Check GPA"), sg.Button("Check Academic Status")]
    ], title="Academic Status", expand_x=True)],

    # Exit button
    [sg.Button("Exit")]
]

# ----------------- Create Window -----------------
window = sg.Window("University Student Management", layout, element_justification="center")

# Store the currently loaded student object
student_obj = None

# ----------------- Event Loop -----------------
while True:
    event, values = window.read()

    # Handle window close or Exit button
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break

    try:
        # -------- Find Student --------
        if event == "Find Student":
            pid = int(values["-PERSON_ID-"])  # Person ID entered
            stype = values["-STUDENT_TYPE-"]  # Selected Student type
            major_thesis = values["-MAJOR_THESIS-"]  # Major (UG) or Thesis (PG)

            # Create correct student object depending on type
            if stype == "Undergraduate":
                student_obj = UndergraduateStudent(person_id=pid, major=major_thesis)
            elif stype == "Graduate":
                student_obj = GraduateStudent(person_id=pid, thesis_title=major_thesis)
            else:
                sg.popup_error("Select a valid student type")
                continue

            # Display loaded student details and enrolled courses
            courses = student_obj.view_grades()
            courses_str = ""
            for semester, sem_courses in courses.items():
                courses_str += f"{semester}:\n"
                for course, grade in sem_courses.items():
                    courses_str += f"  {course}: {grade}\n"
            info_text = (
                f"Loaded {stype} Student:\n"
                f"Name: {student_obj.name}\n"
                f"Person ID: {student_obj.person_id}\n"
                f"Student ID: {student_obj.student_id}\n"
                f"Courses & Grades:\n{courses_str}"
            )
            window["-INFO-"].update(info_text)

        # -------- Enroll in a Course --------
        elif event == "Enroll Course":
            if student_obj:
                try:
                    course_id = int(values["-COURSE_ID-"])
                    semester = values["-SEMESTER-"] or "Fall 2025"

                    # Call updated enroll_course
                    result_msg = student_obj.enroll_course(course_id, semester)

                    # Refresh displayed courses
                    courses = student_obj.view_grades()
                    courses_str = ""
                    for sem, sem_courses in courses.items():
                        courses_str += f"{sem}:\n"
                        for course, grade in sem_courses.items():
                            courses_str += f"  {course}: {grade}\n"

                    window["-INFO-"].update(
                        f"{student_obj.name} Courses & Grades:\n{courses_str}"
                    )

                    sg.popup(result_msg)

                except ValueError:
                    sg.popup_error("Enter valid numeric Course ID.")
                except Exception as e:
                    sg.popup_error(f"Enrollment Error: {e}")
            else:
                sg.popup_error("Find a student first.")

        # -------- Drop a Course --------
        elif event == "Drop Course":
            if student_obj:
                try:
                    course_id = int(values["-COURSE_ID-"])
                    semester = values["-SEMESTER-"] or "Fall 2025"  # Default if empty

                    result_msg = student_obj.drop_course(course_id, semester)

                    # Refresh displayed courses
                    courses = student_obj.view_grades()
                    courses_str = ""
                    for sem, sem_courses in courses.items():
                        courses_str += f"{sem}:\n"
                        for course, grade in sem_courses.items():
                            courses_str += f"  {course}: {grade}\n"

                    window["-INFO-"].update(
                        f"{student_obj.name} Courses & Grades:\n{courses_str}"
                    )

                    sg.popup(result_msg)

                except ValueError:
                    sg.popup_error("Enter a valid numeric Course ID.")
                except Exception as e:
                    sg.popup_error(f"Drop Course Error: {e}")
            else:
                sg.popup_error("Find a student first.")

        # -------- GPA Calculation --------
        elif event == "Check GPA":
            if student_obj:
                gpa = student_obj.calculate_gpa()
                sg.popup(f"{student_obj.name} GPA: {gpa:.2f}")
            else:
                sg.popup_error("Find a student first.")

        # -------- Academic Status --------
        elif event == "Check Academic Status":
            if student_obj:
                status = student_obj.get_academic_status()
                sg.popup(f"{student_obj.name} Academic Status: {status}")
            else:
                sg.popup_error("Find a student first.")

    except Exception as e:
        # Catch any runtime errors and show popup
        sg.popup_error(f"Error: {e}")

# ----------------- Close Window -----------------
window.close()
