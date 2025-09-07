"""
Main script to demonstrate the university hierarchy.
"""

from student import UndergraduateStudent, GraduateStudent, Student
from faculty import Professor, Lecturer, TeachingAssistant
from staff import Staff

if __name__ == "__main__":
    # Create a list of different people in the university
    people = [
        UndergraduateStudent("Alice", 20, "U123", "Computer Science"),
        GraduateStudent("Bob", 25, "G456", "AI in Education"),
        Professor("Dr. Smith", 50, "F001", "Mathematics"),
        Lecturer("Mr. Lee", 40, "F002", "Physics"),
        TeachingAssistant("Charlie", 28, "F003", "Programming 101"),
        Staff("Diana", 35, "Administrative"),
    ]
    s1 = Student("Alice", 20, "U123")

    # Enroll in courses
    s1.enroll_course("Math")
    s1.enroll_course("Physics")
    s1.enroll_course("Chemistry")

    # Assign grades
    # s1.assign_grade("Math", 3.8)
    # s1.assign_grade("Physics", 3.2)
    # s1.assign_grade("Chemistry", 3.9)

    # Drop a course
    s1.drop_course("Physics")

    # Print introduction and academic info
    print(s1.introduce())

    # GPA and status
    print(f"GPA: {s1.calculate_gpa():.2f}")
    print(f"Academic Status: {s1.get_academic_status()}")

    # Demonstrate polymorphism: each person introduces themselves differently
    for person in people:
        print(person.introduce())
