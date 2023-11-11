import sqlite3

def initialize():
    connection = sqlite3.connect("Server.db")
    cursor = connection.cursor()

    cursor.execute('PRAGMA foreign_keys = ON')

    init_script = '''
                    CREATE TABLE IF NOT EXISTS Admin (
                        id VARCHAR PRIMARY KEY NOT NULL,
                        password_hashed VARCHAR(20) NOT NULL,
                        fname VARCHAR NOT NULL,
                        lname VARCHAR,
                        email VARCHAR,
                        contact VARCHAR(10)
                    );

                    CREATE TABLE IF NOT EXISTS Student (
                        id VARCHAR(9) PRIMARY KEY NOT NULL,
                        password_hashed VARCHAR(20) NOT NULL,
                        fname VARCHAR NOT NULL,
                        lname VARCHAR,
                        email VARCHAR,
                        contact VARCHAR(10),
                        batch INTEGER NOT NULL,
                        department_id VARCHAR(4),

                        FOREIGN KEY(department_id) REFERENCES Department(did)
                    );

                    CREATE TABLE IF NOT EXISTS Department (
                        did VARCHAR(4) PRIMARY KEY NOT NULL,
                        dname VARCHAR NOT NULL,
                        hod_id VARCHAR(9),

                        FOREIGN KEY(hod_id) REFERENCES Faculty(id)
                    );

                    CREATE TABLE IF NOT EXISTS Faculty (
                        id VARCHAR(9) PRIMARY KEY NOT NULL,
                        password_hashed VARCHAR(20) NOT NULL,
                        fname VARCHAR NOT NULL,
                        lname VARCHAR,
                        email VARCHAR,
                        contact VARCHAR(10),
                        department_id VARCHAR(4),

                        FOREIGN KEY(department_id) REFERENCES Department(did)
                    );

                    CREATE TABLE IF NOT EXISTS FacultyAdvisor (
                        fid VARCHAR(9) PRIMARY KEY NOT NULL,
                        batch INTEGER NOT NULL CHECK(batch >= 1900 AND batch <= 2100),

                        FOREIGN KEY(fid) REFERENCES Faculty(id)
                    );

                    CREATE TABLE IF NOT EXISTS Course (
                        cid VARCHAR(7) PRIMARY KEY NOT NULL,
                        cname VARCHAR NOT NULL,
                        faculty VARCHAR(9),

                        FOREIGN KEY(faculty) REFERENCES Faculty(id)
                    );

                    CREATE TABLE IF NOT EXISTS Application (
                        course_id VARCHAR(7) NOT NULL,
                        student_id VARCHAR(9) NOT NULL,

                        PRIMARY KEY(course_id, student_id),
                        FOREIGN KEY(course_id) REFERENCES Course(cid),
                        FOREIGN KEY(student_id) REFERENCES Student(id)
                    );

                    CREATE TABLE IF NOT EXISTS Rejected (
                        course_id VARCHAR(7) NOT NULL,
                        student_id VARCHAR(9) NOT NULL,

                        PRIMARY KEY(course_id, student_id),
                        FOREIGN KEY(course_id) REFERENCES Course(cid),
                        FOREIGN KEY(student_id) REFERENCES Student(id)
                    );

                    CREATE TABLE IF NOT EXISTS Accepted (
                        course_id VARCHAR(7) NOT NULL,
                        student_id VARCHAR(9) NOT NULL,

                        PRIMARY KEY(course_id, student_id),
                        FOREIGN KEY(course_id) REFERENCES Course(cid),
                        FOREIGN KEY(student_id) REFERENCES Student(id)
                    );
                '''

    cursor.executescript(init_script)
    
    cursor.close()
    connection.close()