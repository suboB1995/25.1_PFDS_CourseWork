import sqlite3

# ----------------------------Connect to SQLite Database----------------------------
db_file = "university_system.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON;")

# ----------------------------Create Tables----------------------------
schema_script = """
CREATE TABLE IF NOT EXISTS Person (
    person_id     INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE,
    phone_number  TEXT,
    role          TEXT,
    dob           TEXT,
    address       TEXT
);

CREATE TABLE IF NOT EXISTS Department (
    department_id INTEGER PRIMARY KEY,
    name          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Student (
    student_id    INTEGER PRIMARY KEY,
    person_id     INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    level         TEXT,
    major         TEXT,
    thesis_title  TEXT,
    supervisor_id INTEGER DEFAULT NULL,
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Department(department_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Staff (
    staff_id      INTEGER PRIMARY KEY,
    person_id     INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Department(department_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Faculty (
    faculty_id    INTEGER PRIMARY KEY,
    person_id     INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    type          TEXT,
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Department(department_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS SecureStudentRecord (
    record_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    gpa        REAL,
    status     TEXT,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Course (
    course_id       INTEGER PRIMARY KEY,
    department_id   INTEGER NOT NULL,
    name            TEXT NOT NULL,
    credits         INTEGER,
    enrollment_limit INTEGER,
    faculty_id      INTEGER,
    FOREIGN KEY (department_id) REFERENCES Department(department_id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Enrollment (
    enrollment_id INTEGER PRIMARY KEY,
    student_id    INTEGER NOT NULL,
    course_id     INTEGER NOT NULL,
    semester      TEXT,
    grade         TEXT,
    gpa_points    REAL,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Course(course_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS FacultyWorkload (
    workload_id    INTEGER PRIMARY KEY,
    faculty_id     INTEGER NOT NULL UNIQUE,
    teaching_hours INTEGER,
    research_hours INTEGER,
    support_hours  INTEGER,
    total_hours    INTEGER,
    FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id) ON DELETE CASCADE
);
    
CREATE TABLE IF NOT EXISTS CoursePrerequisites (
    id                  INTEGER PRIMARY KEY,
    course_id           INTEGER NOT NULL,
    prereq_course_id    INTEGER NOT NULL,
    FOREIGN KEY(course_id) REFERENCES Course(course_id) ON DELETE CASCADE,
    FOREIGN KEY(prereq_course_id) REFERENCES Course(course_id) ON DELETE CASCADE
);   

"""

cursor.executescript(schema_script)
conn.commit()

# ----------------------------Insert Sample Data----------------------------
# Departments
departments = [
    (1, "Computer Science"),
    (2, "Mathematics"),
    (3, "Physics")
]
cursor.executemany("INSERT OR IGNORE INTO Department VALUES (?, ?);", departments)

# Person
persons = [
    (1, "Aruni Perera", "aruni.p@example.lk", "011-5551000", "Student", "2000-01-15", "123 Galpotha Mawatha, Colombo"),
    (2, "Samantha Kodiyella", "samantha.k@example.lk", "011-5551001", "Faculty", "1980-05-22", "456 Nagarika Mawatha, Kegalle"),
    (3, "Dinushi Jayasekara", "dinushi.j@example.lk", "011-5551002", "Student", "2001-07-30", "789 Pine Mawatha, Galle"),
    (4, "Sunil Wickramasinghe", "sunil.v@example.lk", "011-5551003", "Admin", "1980-05-22", "678 Avi Nivasa Mawatha, Maharagama"),
    (5, "Chamara Fernando", "chamara.p@example.lk", "011-5551004", "Faculty", "1975-12-10", "321 Oak Mawatha, Nuwara Eliya"),
    (6, "Ashoka Navaratne", "ashoka.n@example.lk", "011-5551005", "Faculty", "1978-03-14", "654 Maple Mawatha, Kadugoda")
]

cursor.executemany("INSERT OR IGNORE INTO Person VALUES (?, ?, ?, ?, ?, ?, ?);", persons)

# Students
students = [
    (1, 1, 1, "Undergraduate","Computer Science",None, None),
    (2, 3, 2, "Graduate","Mathematics","Differentiation",2)
]
cursor.executemany("INSERT OR IGNORE INTO Student VALUES (?, ?, ?, ?, ?, ?, ?);", students)

# Faculty
faculty = [
    (1, 2, 1, "Professor"),
    (2, 5, 2, "Lecturer"),
    (3, 6, 3, "Teaching Assistant")
]
cursor.executemany("INSERT OR IGNORE INTO Faculty VALUES (?, ?, ?, ?);", faculty)

# Courses
courses = [
    (1, 1, 'Introduction to Programming', 3, 50, 1),
    (2, 1, 'Data Structures', 3, 40, 2),
    (3, 1, 'Algorithms', 3, 35, 1),
    (4, 1, 'Databases', 3, 40, 2),
    (5, 1, 'Advanced Databases', 3, 30, 1),
    (6, 1, 'Operating Systems', 3, 35, 2),
    (7, 2, 'Computer Networks', 3, 35, 1),
    (8, 2, 'Distributed Systems', 3, 30, 2),
    (9, 2, 'Network Security', 3, 30, 1),
    (10, 1, 'Software Engineering', 3, 40, 2),
    (11, 1, 'Capstone Project', 3, 20, 1)
]
cursor.executemany("INSERT OR IGNORE INTO Course VALUES (?, ?, ?, ?, ?, ?);", courses)

# Enrollments
enrollments = [
    (1, 1, 1, "Fall 2025", "A", 4.0),
    (2, 2, 2, "Fall 2025", "B", 3.0),
    (3, 1, 3, "Summer 2025", "A", 4.0),
    (4, 2, 4, "Winter 2025", "B", 3.0)
]
cursor.executemany("INSERT OR IGNORE INTO Enrollment VALUES (?, ?, ?, ?, ?, ?);", enrollments)

#CoursePrerequisites
course_prereqs = [
    (1, 2, 1),  # Data Structures → Intro to Programming
    (2, 3, 2),  # Algorithms → Data Structures
    (3, 4, 1),  # Databases → Intro to Programming
    (4, 5, 4),  # Advanced Databases → Databases
    (5, 6, 3),  # Operating Systems → Algorithms
    (6, 7, 3),  # Computer Networks → Algorithms
    (7, 8, 6),  # Distributed Systems → Operating Systems
    (8, 9, 7),  # Network Security → Computer Networks
    (9, 10, 3),  # Software Engineering → Algorithms
    (10, 11, 10),  # Capstone Project → Software Engineering
]
cursor.executemany("INSERT OR IGNORE INTO CoursePrerequisites VALUES (?, ?, ?)",course_prereqs)

# Commit sample data
conn.commit()

# ----------------------------Execute Query----------------------------
cursor.execute("""
SELECT s.student_id, p.name, d.name AS department, c.name AS course, e.grade
FROM Student s
JOIN Person p ON s.person_id = p.person_id
JOIN Department d ON s.department_id = d.department_id
LEFT JOIN Enrollment e ON s.student_id = e.student_id
LEFT JOIN Course c ON e.course_id = c.course_id;
""")

rows = cursor.fetchall()
for row in rows:
    print(row)

# ----------------------------Close Connection----------------------------
conn.close()
print("Database setup completed")
