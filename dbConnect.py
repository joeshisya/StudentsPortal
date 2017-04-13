import datetime
import gc

import MySQLdb
from passlib.hash import sha512_crypt


class DbConnect(object):
    def __init__(self, database):
        self.conn = MySQLdb.connect(host="localhost", user="developer", passwd="secret", db=database)
        self.c = self.conn.cursor(MySQLdb.cursors.DictCursor)

    # Checks if a user exists
    # Returns True if they exist else False
    def user_exists(self, attempted_reg_no):
        query = "SELECT * FROM login WHERE registration_number = '{0}'".format(attempted_reg_no)
        self.c.execute(query)

        result = self.c.fetchone()
        self.close_db()

        return True if result else False

    # Verifies the passed credentials
    # Returns True if they are valid otherwise false
    def confirm_account(self, attempted_reg_no, attempted_password):
        query = "SELECT * FROM login WHERE registration_number = '{0}'".format(attempted_reg_no)
        self.c.execute(query)

        result = self.c.fetchone()
        self.close_db()

        if not result:
            return False

        if sha512_crypt.verify(attempted_password, result['user_password']):
            return True

        else:
            return False

    # Adds account to database
    def add_account(self, details):
        query = """INSERT INTO student_details (registration_number, first_name, last_name, other_names, mode_of_admission,
                    faculty, course_level, course, email, phone_number, gender, date_of_birth, registration_date, 
                    current_year, current_semester, disabled) 
                    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', 
                    '{12}', '{13}', '{14}', '{15}')
                """.format(
                    details.get('registration_number'), details.get('first_name'), details.get('last_name'),
                    details.get('other_names'), details.get('mode_of_admission'), details.get('level'),
                    details.get('faculty'), details.get('course'), details.get('email'), details.get('phone_number'),
                    details.get('gender'), details.get('dob'), datetime.datetime.now(), details.get('year'),
                    details.get('semester'), 1)

        self.c.execute(query)
        self.conn.commit()

        # This is the default password given to all users
        user_password = "password"

        # Encrypt the password
        user_password = sha512_crypt.encrypt(user_password)

        query = """INSERT INTO login (registration_number, email, user_password) VALUES ('{0}', '{1}', '{2}')""".format(
                    details['registration_number'], details['email'], user_password
                )

        self.c.execute(query)
        self.conn.commit()
        self.close_db()

    # Fetches the students details from the datbase
    def get_student_details(self, reg_no):
        query = "SELECT * FROM student_details WHERE registration_number='{0}'".format(reg_no)
        self.c.execute(query)

        result = self.c.fetchone()
        self.close_db()

        return result

    # Gets a list of the documents from the database
    # Returns a list of the available files
    # Files stored as dictionaries
    def get_documents(self, course, year, sem):
        query = "SELECT * FROM notes WHERE course='{0}' and year={1} and semester={2}".format(course, year, sem)
        self.c.execute(query)

        results = self.c.fetchall()
        self.close_db()

        return results

    # Checks for available hostel rooms
    def available_hostels(self, gender):
        query = "SELECT * FROM hostels WHERE gender='{0}' AND available_spaces > 0".format(gender)
        self.c.execute(query)

        results = self.c.fetchall()
        self.close_db()

        return results

    # Reduces hostel spaces by one
    def occupied_hostel(self, hostel_name):
        query = "UPDATE hostels SET available_spaces=available_spaces-1 WHERE hostel_name='{0}'".format(hostel_name)
        self.c.execute(query)
        self.close_db()

    # Adds the student to the selected hostel
    def assign_hostel(self, hostel_name, registration_number):
        query = "UPDATE student_details SET hostel='{0}' WHERE registration_number='{1}'".format(hostel_name,
                                                                                                 registration_number)
        self.c.execute(query)
        self.close_db()

    # Adds password reset code to database
    # Code will be used to ensure that the correct user is changing the password
    def add_password_reset_code(self, reset_code, registration_number):
        query = "INSERT INTO password_reset (reset_code, registration_number) VALUES('{0}', '{1}')".format(
                    reset_code, registration_number
        )
        self.c.execute(query)
        self.close_db()

    # Confirms whether the password reset code is in the database
    def is_valid_password_reset_link(self, reset_code):
        query = "SELECT * FROM password_reset WHERE reset_code='{0}'".format(reset_code)
        self.c.execute(query)
        result = self.c.fetchone()

        query = "DELETE FROM password_reset WHERE reset_code='{0}'".format(reset_code)
        self.c.execute(query)

        self.close_db()

        return result

    # Change the users password
    def change_password(self, reg_no, new_password):
        new_password = sha512_crypt.encrypt(new_password)

        query = "UPDATE login SET user_password='{0}' WHERE registration_number='{1}'".format(new_password, reg_no)
        self.c.execute(query)

        self.close_db()

    # Get the timetable
    def get_timetable(self, student_details):
        query = """SELECT timetable.*, units.unit_code FROM timetable LEFT JOIN units ON 
                    timetable.unit_id=units.unit_id WHERE units.course='{0}' AND  units.year='{1}' AND 
                    units.semester='{2}'""".format(
                        student_details['course'], student_details['current_year'], student_details['current_semester']
        )
        self.c.execute(query)

        results = self.c.fetchall()
        self.close_db()

        return results

    # Close the database
    def close_db(self):
        self.c.close()
        self.conn.close()
        gc.collect()
