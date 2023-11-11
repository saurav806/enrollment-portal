from flask import Flask
from flask import request, redirect, render_template, url_for, session

from db_init import initialize
from faculty_functionality import Faculty
from admin_functionality import Admin
from student_functionality import Student


app = Flask(__name__)
app.secret_key = b'F#%JGTs@WjzHGGLSidT6ZVz9'

initialize()

@app.route("/")
def index():
    return render_template('index.html')


##### AUTH PAGES #####

@app.route("/login_admin", methods=['GET', 'POST'])
def login_admin():
    admin = Admin()

    error = None
    if request.method == 'POST':
        admin_id = request.form['username']
        password = request.form['password']

        return_message = admin.admin_login(admin_id, password)
        if return_message == 'Successfully Logged In':
            session['id'] = admin_id.lower()
            session['user_type'] = 'admin'
            session['username'] = admin.get_details(admin_id)[2]      # 2nd index contains fname
            return redirect(url_for('admin_dash'))
        else:
            error = return_message

    return render_template('login_admin.html', error = error)


@app.route("/register_faculty", methods=['GET', 'POST'])
def register_faculty():
    faculty = Faculty()
    department_list = faculty.return_departments()

    error = None
    if request.method == 'POST':
        data = {}
        data['id'] = request.form.get('id')
        data['password'] = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        data['fname'] = request.form.get('first-name')
        data['lname'] = request.form.get('last-name')
        data['email'] = request.form.get('email')
        data['contact'] = request.form.get('contact-number')
        data['department_id'] = request.form.get('department-id')

        if data['password'] != confirm_password:
            error = 'Password does not match Confirm Password'
        else:
            return_message = faculty.register(data)
            if return_message == "Successfully Registered":
                session['id'] = data['id'].lower()
                session['user_type'] = 'faculty'
                session['username'] = data['fname']
                return redirect(url_for('index'))
            else:
                error = return_message

    return render_template('register_faculty.html', department_list = department_list, error = error)


@app.route("/login_faculty", methods=['GET', 'POST'])
def login_faculty():
    faculty = Faculty()

    error = None
    if request.method == 'POST':
        faculty_id = request.form['username']
        password = request.form['password']

        faculty_id = faculty_id.lower()
        return_message = faculty.faculty_login(faculty_id, password)
        if return_message == 'Successfully Logged In':
            session['id'] = faculty_id
            session['user_type'] = 'faculty'
            session['username'] = faculty.get_details(faculty_id)[2]      # 2nd index contains fname

            if faculty.is_advisor(faculty_id):
                session['is_advisor'] = True
            else:
                session['is_advisor'] = False
                
            return redirect(url_for('index'))
        else:
            error = return_message

    return render_template('login_faculty.html', error = error)


@app.route("/register_student", methods=['GET', 'POST'])
def register_student():
    student = Student()
    department_list = student.return_departments()

    error = None
    if request.method == 'POST':
        data = {}
        data['id'] = request.form.get('id')
        data['password'] = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        data['fname'] = request.form.get('first-name')
        data['lname'] = request.form.get('last-name')
        data['email'] = request.form.get('email')
        data['contact'] = request.form.get('contact-number')
        data['batch'] = request.form.get('batch')
        data['department_id'] = request.form.get('department-id')

        if data['password'] != confirm_password:
            error = 'Password does not match Confirm Password'
        else:
            return_message = student.register(data)
            if return_message == "Successfully Registered":
                session['id'] = data['id'].lower()
                session['user_type'] = 'student'
                session['username'] = data['fname']
                return redirect(url_for('student_dash'))
            else:
                error = return_message

    return render_template('register_student.html', department_list = department_list, error = error)


@app.route("/login_student", methods=['GET', 'POST'])
def login_student():
    student = Student()

    error = None
    if request.method == 'POST':
        student_id = request.form['username']
        password = request.form['password']

        return_message = student.student_login(student_id, password)
        if return_message == 'Successfully Logged In':
            session['id'] = student_id.lower()
            session['user_type'] = 'student'
            session['username'] = student.get_details(student_id.lower())[2]      # 2nd index contains fname
            return redirect(url_for('student_dash'))
        else:
            error = return_message

    return render_template('login_student.html', error = error)


@app.route("/logout")
def logout():
    session.pop('id')
    return redirect(url_for('index'))


##### CORE FUNCTIONALITY #####

@app.route('/admin_dash')
def admin_dash():
    return render_template('admin_dash.html')

options_data = {
    'A': ['Option A1', 'Option A2', 'Option A3'],
    'B': ['Option B1', 'Option B2', 'Option B3'],
    'C': ['Option C1', 'Option C2', 'Option C3']
}

@app.route('/update_hod', methods=['GET', 'POST'])
def update_hod():
    faculty = Faculty()
    admin = Admin()

    departments_data = {}
    departments = faculty.return_departments()

    for department in departments:
        faculty_list = faculty.get_faculty_list(department[0])  # department[0] returns the id for the department
        # The key of the dictionary is the department name and id, the value is the faculty list of that department
        faculty_ids = [(li[0], li[2]+' '+li[3]) for li in faculty_list]
        departments_data[department[1] + '  (' + department[0] + ')'] = faculty_ids    
        
    selected_option = None
    selected_sub_option = None

    message = None
    if request.method == 'POST':
        selected_option = request.form.get('option')
        selected_sub_option = request.form.get('sub_option')
        if selected_sub_option != None:
            res = admin.promote_to_hod(selected_sub_option)        # The faculty id of the selected sub-option
            if res:
                message = "Department Head Updated Successfully"
            else:
                message = "Unable to Update HoD"

    return render_template('update_hod.html', departments_data = departments_data, message = message,
                            selected_option = selected_option, selected_sub_option = selected_sub_option)


@app.route('/elevate_faculty', methods = ['GET', 'POST'])
def elevate_faculty():
    admin = Admin()
    available_years = admin.get_batch_years()

    faculty = Faculty()
    faculty_list = faculty.get_non_fa_faculties()

    message = None
    if request.method == 'POST':
        faculty_id = request.form['faculty_id']
        batch_year = request.form['batch']

        message = admin.elevate_faculty(faculty_id, batch_year)

    return render_template('elevate_faculty.html', message = message,
                           years = available_years, faculty_list = faculty_list)


@app.route('/create_course', methods = ['GET', 'POST'])
def create_course():
    faculty = Faculty()
    admin = Admin()

    departments_data = {}
    departments = faculty.return_departments()

    for department in departments:
        faculty_list = faculty.get_faculty_list(department[0])  # department[0] returns the id for the department
        # The key of the dictionary is the department name and id, the value is the faculty list of that department
        faculty_ids = [(li[0], li[2]+' '+li[3]) for li in faculty_list]
        departments_data[department[1] + '  (' + department[0] + ')'] = faculty_ids    
        
    department_string = None
    faculty_id = None

    res = None
    if request.method == 'POST':
        department_string = request.form.get('option')
        faculty_id = request.form.get('sub_option')
        if faculty_id != None:
            course_id = request.form.get('course_id')
            course_name = request.form.get('course_name')
            res = admin.create_course(course_id, course_name, faculty_id) 

    return render_template('create_course.html', departments_data = departments_data, message = res,
                            department_string = department_string, faculty_id = faculty_id)


@app.route('/course_register', methods = ['GET', 'POST'])
def course_register():
    student_id = None
    if 'id' in session and session['user_type'] == 'student':
        student_id = session['id']
    else:
        return redirect(url_for('login_student'))


    student = Student()

    available_courses = student.get_available_courses(session['id'])

    message = None
    if request.method == 'POST':
        course_id = request.form['course_id']
        message = student.enroll(student_id, course_id)

    return render_template('course_register.html', message = message,
                           courses = available_courses)


@app.route('/student_dash')
def student_dash():
    student_id = None
    if 'id' in session and session['user_type'] == 'student':
        student_id = session['id']
    else:
        return redirect(url_for('login_student'))
    
    student = Student()
    
    applied_courses = student.get_applied_courses(student_id)
    accepted_courses = student.get_accepted_courses(student_id)
    rejected_courses = student.get_rejected_courses(student_id)

    return render_template('student_dash.html', applied_courses = applied_courses, 
                           accepted_courses = accepted_courses, rejected_courses = rejected_courses)


@app.route('/active_registrations')
def active_registrations():
    faculty_id = None
    if 'id' in session and session['user_type'] == 'faculty' and session['is_advisor']:
        faculty_id = session['id']        
    else:
        return redirect(url_for('login_faculty'))
    
    faculty = Faculty()
    registrations = faculty.get_active_registrations(faculty_id)

    return render_template('active_registrations.html', registrations = registrations)


@app.route('/accept_registration', methods = ['GET', 'POST'])
def accept_registration():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']

        faculty = Faculty()
        faculty.accept_registration(course_id, student_id)

    return redirect(url_for('active_registrations'))


@app.route('/reject_registration', methods = ['GET', 'POST'])
def reject_registration():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']

        faculty = Faculty()
        faculty.reject_registration(course_id, student_id)

    return redirect(url_for('active_registrations'))


@app.route('/faculty_course_list')
def faculty_course_list():
    faculty_id = None
    if 'id' in session and session['user_type'] == 'faculty':
        faculty_id = session['id']
    else:
        return redirect(url_for('index'))
    
    faculty = Faculty()
    course_list = faculty.get_course_list(faculty_id)

    return render_template('faculty_course_list.html', courses = course_list)


@app.route('/course/<course_id>')
def course_details(course_id):
    if 'id' in session:
        if session['user_type'] == 'faculty' or session['user_type'] == 'admin':
            pass
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

    faculty = Faculty()
    data = faculty.course_details(course_id)

    return render_template('course_detail.html', data = data)


@app.route('/faculty_list')
def faculty_list():
    if 'id' in session:
        if session['user_type'] == 'admin':
            pass
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    
    faculty = Faculty()
    data = faculty.get_all_faculties()

    return render_template('faculty_list.html', data = data)


@app.route('/delete_faculty', methods = ['GET', 'POST'])
def delete_faculty():
    if 'id' in session:
        if session['user_type'] == 'admin':
            pass
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    
    faculty = Faculty()
    message = faculty.delete_faculty(request.form['faculty_id'])

    status = None
    if message == 'Faculty Deleted Successfully':
        status = 'Success'
    else:
        status = 'Failed'

    return render_template('faculty_deleted_message.html', message = message, status = status)