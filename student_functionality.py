import sqlite3
import bcrypt

class Student:
    def register(self, student_data):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        cursor.execute('SELECT id, email FROM Student')

        rows = cursor.fetchall()
        id_values = [row[0] for row in rows]
        email_values = [row[1] for row in rows]

        cursor.execute('SELECT did FROM Department')
        rows = cursor.fetchall()
        did_values = [row[0] for row in rows]

        return_message = ""

        if student_data['id'] in id_values:
            return_message = "Student Already Registered"
        elif student_data['email'] in email_values:
            return_message = "Email is Already Registered"
        elif student_data['department_id'] not in did_values:
            return_message = "Department does not Exist"
        else:
            password = bytes(student_data['password'], 'utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            cursor.execute('INSERT INTO Student VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
                student_data['id'].lower(), hashed_password, student_data['fname'], 
                student_data['lname'], student_data['email'], student_data['contact'],
                student_data['batch'], student_data['department_id']
            ))

            connection.commit()
            return_message = "Successfully Registered"

        cursor.close()
        connection.close()
        return return_message
            
        
    def student_login(self, student_id, password):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        student_id = student_id.lower()
        res = cursor.execute('SELECT * FROM Student WHERE id = ?', (student_id, ))
        row = res.fetchone()

        cursor.close()
        connection.close()

        if row != None:
            password = bytes(password, 'utf-8')
            if(bcrypt.checkpw(password, row[1])):
                return 'Successfully Logged In'
            else:
                return 'Incorrect Password'
        else:
            return 'Incorrect Username'
        

    def return_departments(self):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        res = cursor.execute('SELECT * FROM Department')
        data = res.fetchall()

        cursor.close()
        connection.close()

        return data
    

    def get_details(self, student_id):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        res = cursor.execute('SELECT * FROM Student WHERE id = ?', (student_id, ))
        row = res.fetchone()

        cursor.close()
        connection.close()

        return row
    

    def enroll(self, student_id, course_id):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        # Student ID should exist
        # Course ID should exist
        # Registration shouldn't already exist in either of the tables: Application, Accepted, Rejected

        res = cursor.execute('SELECT COUNT(*) FROM Student WHERE id = ?', (student_id, ))
        student_count = res.fetchone()[0]

        res = cursor.execute('SELECT COUNT(*) FROM Course WHERE cid = ?', (course_id, ))
        course_count = res.fetchone()[0]

        return_str = ""
        if student_count == 0:
            return_str = "Student ID is Incorrect"
        elif course_count == 0:
            return_str = "Course ID is Incorrect"
        else:
            res = cursor.execute('SELECT COUNT(*) FROM Accepted WHERE course_id = ? AND student_id = ?', 
                                 (course_id, student_id))
            count1 = res.fetchone()[0]

            res = cursor.execute('SELECT COUNT(*) FROM Rejected WHERE course_id = ? AND student_id = ?', 
                                 (course_id, student_id))
            count2 = res.fetchone()[0]

            res = cursor.execute('SELECT COUNT(*) FROM Application WHERE course_id = ? AND student_id = ?', 
                                 (course_id, student_id))
            count3 = res.fetchone()[0]

            if count1 != 0:
                return_str = "You are Already Registered into this Course"
            elif count2 != 0:
                return_str = "Your Application for this Course is Rejected"
            elif count3 != 0:
                return_str = "Your Application in this Course is Processing"
            else:
                res = cursor.execute('INSERT INTO APPLICATION VALUES(?, ?)', (course_id, student_id))
                connection.commit()
                return_str = "Registration Request Successful"

        cursor.close()
        connection.close()
        return return_str
    

    def get_available_courses(self, student_id):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        # Test this query thoroughly later
        query = '''
            SELECT c.cid, c.cname, c.faculty
            FROM Course c
            LEFT JOIN Application a ON c.cid = a.course_id AND a.student_id = ?
            LEFT JOIN Accepted ac ON c.cid = ac.course_id AND ac.student_id = ?
            LEFT JOIN Rejected r ON c.cid = r.course_id AND r.student_id = ?
            WHERE a.course_id IS NULL AND ac.course_id IS NULL AND r.course_id IS NULL;
        '''
        res = cursor.execute(query, (student_id, student_id, student_id))
        rows = res.fetchall()

        cursor.close()
        connection.close()

        return rows
    

    def get_applied_courses(self, student_id):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        query = '''
            SELECT a.course_id, c.cname, c.faculty, f.fname || ' ' || f.lname AS full_name
            FROM Application a 
            JOIN Course c ON a.course_id = c.cid
            JOIN Faculty f ON c.faculty = f.id
            WHERE a.student_id = ?
        '''
        res = cursor.execute(query, (student_id, ))
        rows = res.fetchall()

        cursor.close()
        connection.close()

        return rows
    

    def get_accepted_courses(self, student_id):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        query = '''
            SELECT a.course_id, c.cname, c.faculty, f.fname || ' ' || f.lname AS full_name
            FROM Accepted a 
            JOIN Course c ON a.course_id = c.cid
            JOIN Faculty f ON c.faculty = f.id
            WHERE a.student_id = ?
        '''
        res = cursor.execute(query, (student_id, ))
        rows = res.fetchall()

        cursor.close()
        connection.close()

        return rows
    

    def get_rejected_courses(self, student_id):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        query = '''
            SELECT a.course_id, c.cname, c.faculty, f.fname || ' ' || f.lname AS full_name
            FROM Rejected a 
            JOIN Course c ON a.course_id = c.cid
            JOIN Faculty f ON c.faculty = f.id
            WHERE a.student_id = ?
        '''
        res = cursor.execute(query, (student_id, ))
        rows = res.fetchall()

        cursor.close()
        connection.close()

        return rows
    

def __main__():
    # student = Student()
    # print(student.get_rejected_courses('m210655ca'))
    pass

if __name__ == '__main__':
    __main__()