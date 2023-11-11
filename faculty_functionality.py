import sqlite3
import bcrypt

class Faculty:
    def register(self, faculty_data):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        cursor.execute('SELECT id, email FROM Faculty')

        rows = cursor.fetchall()
        id_values = [row[0] for row in rows]
        email_values = [row[1] for row in rows]

        cursor.execute('SELECT did FROM Department')
        rows = cursor.fetchall()
        did_values = [row[0] for row in rows]

        return_message = ""

        if faculty_data['id'] in id_values:
            return_message = "Faculty Already Registered"
        elif faculty_data['email'] in email_values:
            return_message = "Email is Already Registered"
        elif faculty_data['department_id'] not in did_values:
            return_message = "Department does not Exist"
        else:
            password = bytes(faculty_data['password'], 'utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            cursor.execute('INSERT INTO Faculty VALUES (?, ?, ?, ?, ?, ?, ?)', (
                faculty_data['id'].lower(), hashed_password, faculty_data['fname'], 
                faculty_data['lname'], faculty_data['email'], faculty_data['contact'],
                faculty_data['department_id']
            ))

            connection.commit()
            return_message = "Successfully Registered"

        cursor.close()
        connection.close()
        return return_message
            
        
    def faculty_login(self, faculty_id, password):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        faculty_id = faculty_id.lower()
        res = cursor.execute('SELECT * FROM Faculty WHERE id = ?', (faculty_id, ))
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
    

    def get_details(self, faculty_id):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        res = cursor.execute('SELECT * FROM Faculty WHERE id = ?', (faculty_id, ))
        row = res.fetchone()

        cursor.close()
        connection.close()

        return row
    

    def get_faculty_list(self, department_id):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        res = cursor.execute('SELECT * FROM Faculty WHERE department_id = ?', (department_id, ))
        rows = res.fetchall()

        cursor.close()
        connection.close()

        return rows
    

    def get_non_fa_faculties(self):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        res = cursor.execute('SELECT * FROM Faculty WHERE id NOT IN (SELECT fid FROM FacultyAdvisor)')
        rows = res.fetchall()

        cursor.close()
        connection.close()

        return rows
    

    def is_advisor(self, faculty_id):
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        res = cursor.execute('SELECT COUNT(*) FROM FacultyAdvisor WHERE fid = ?', (faculty_id, ))
        count = res.fetchone()[0]

        cursor.close()
        connection.close()

        if count == 0:
            return False
        else:
            return True
        

    def get_active_registrations(self, faculty_id):
        if not self.is_advisor(faculty_id):
            return 'Should be a Faculty Advisor'
        
        connection = sqlite3.connect("Server.db")
        cursor = connection.cursor()

        res = cursor.execute('SELECT batch FROM FacultyAdvisor WHERE fid = ?', (faculty_id, ))
        batch = res.fetchone()[0]

        query = '''
            SELECT a.student_id, s.fname || ' ' || s.lname, a.course_id, c.cname, f.fname || ' ' || f.lname
            FROM Application a 
            JOIN Student s ON a.student_id = s.id
            JOIN Course c ON a.course_id = c.cid
            JOIN Faculty f ON c.faculty = f.id
            WHERE s.batch = ?;
        '''
        res = cursor.execute(query, (batch, ))
        rows = res.fetchall()

        return rows


    def accept_registration(self, course_id, student_id):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        res = cursor.execute('SELECT COUNT(*) FROM Application WHERE course_id = ? AND student_id = ?', 
                             (course_id, student_id))
        count = res.fetchone()[0]

        return_str = ""
        if count == 0:
            return_str = 'Incorrect Application Details'
        else:
            cursor.execute('DELETE FROM Application WHERE course_id = ? AND student_id = ?', (course_id, student_id))
            cursor.execute('INSERT INTO Accepted VALUES(?, ?)', (course_id, student_id))
            connection.commit()
            return_str = 'Registration Accepted'

        cursor.close()
        connection.close()

        return return_str
    

    def reject_registration(self, course_id, student_id):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        res = cursor.execute('SELECT COUNT(*) FROM Application WHERE course_id = ? AND student_id = ?', 
                             (course_id, student_id))
        count = res.fetchone()[0]

        return_str = ""
        if count == 0:
            return_str = 'Incorrect Application Details'
        else:
            cursor.execute('DELETE FROM Application WHERE course_id = ? AND student_id = ?', (course_id, student_id))
            cursor.execute('INSERT INTO Rejected VALUES(?, ?)', (course_id, student_id))
            connection.commit()
            return_str = 'Registration Rejected'

        cursor.close()
        connection.close()

        return return_str
    

    # Returns a dictionary containing course_id, course_name, faculty_id, faculty_name, and student_list 
    def course_details(self, course_id):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        query = '''
            SELECT c.cid, c.cname, c.faculty, f.fname || ' ' || f.lname
            FROM course c
            JOIN faculty f ON c.faculty = f.id
            WHERE c.cid = ?;
        '''
        res = cursor.execute(query, (course_id, ))
        row = res.fetchone()

        data = {}
        data['course_id'] = row[0]
        data['course_name'] = row[1]
        data['faculty_id'] = row[2]
        data['faculty_name'] = row[3]

        query = '''
            SELECT s.id, s.fname || ' ' || s.lname, s.email, s.batch
            FROM Accepted a
            JOIN Student s ON a.student_id = s.id
            WHERE a.course_id = ?;
        '''
        res = cursor.execute(query, (course_id, ))
        rows = res.fetchall()

        data['student_list'] = rows

        cursor.close()
        connection.close()

        return data
    

    def get_course_list(self, faculty_id):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        query = '''
            SELECT cid, cname, (SELECT COUNT(*) FROM Accepted a WHERE a.course_id = c.cid)
            FROM course c
            WHERE faculty = ?
        '''

        res = cursor.execute(query, (faculty_id, ))
        rows = res.fetchall()

        cursor.close()
        connection.close()

        return rows
    

    def get_all_faculties(self):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        query = '''
            SELECT f.id, f.fname, f.lname, f.email, f.contact, d.dname 
            FROM Faculty f JOIN Department d
            ON f.department_id = d.did
        '''
    
        res = cursor.execute(query)
        rows = res.fetchall()

        return rows
    

    def delete_faculty(self, faculty_id):
        connection = sqlite3.connect('Server.db')
        cursor = connection.cursor()

        query = '''
            SELECT COUNT(*) FROM Course WHERE faculty = ?
        '''
    
        res = cursor.execute(query, (faculty_id, ))
        count = res.fetchone()[0]

        if count > 0:
            return 'Faculty Teaches a Course'

        query = '''
            SELECT COUNT(*) FROM Department WHERE hod_id = ?
        '''
    
        res = cursor.execute(query, (faculty_id, ))
        count = res.fetchone()[0]

        if count > 0:
            return 'Faculty is HOD of a Department'
        
        query = '''
            SELECT COUNT(*) FROM FacultyAdvisor WHERE fid = ?
        '''
    
        res = cursor.execute(query, (faculty_id, ))
        count = res.fetchone()[0]

        if count > 0:
            return 'Faculty is Faculty Advisor'
        

        query = '''
            DELETE FROM Faculty WHERE id = ?
        '''
    
        res = cursor.execute(query, (faculty_id, ))
        connection.commit()
        
        return 'Faculty Deleted Successfully'


def __main__():
    faculty = Faculty()
    print(faculty.delete_faculty('cs569874e'))
    # pass

if __name__ == '__main__':
    __main__()