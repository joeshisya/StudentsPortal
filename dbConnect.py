import datetime
import gc

import MySQLdb
from passlib.hash import sha512_crypt


class DbConnect(object):
    """
    Opens a connection to the database
    """

    def __init__(self, database):
        self.conn = MySQLdb.connect(host="localhost", user="developer", passwd="secret", db=database)
        self.c = self.conn.cursor(MySQLdb.cursors.DictCursor)

    def user_exists(self, attempted_reg_no):
        """
        Checks if a user exists, Returns True if they exist else False
        :param attempted_reg_no: Users registration number
        :return: 
        """

        query = "SELECT * FROM login WHERE registration_number = '{0}'".format(attempted_reg_no)
        self.c.execute(query)

        result = self.c.fetchone()
        self.close_db()

        return True if result else False

    def confirm_account(self, attempted_reg_no, attempted_password):
        """
        Verifies the passed credentials. Returns True if they are valid otherwise false 
        :param attempted_reg_no: The students registration number
        :param attempted_password: The attempted password
        :return: 
        """

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

    def add_account(self, details):
        """
        Adds account to database 
        :param details: Dictionary containing the students details
        :return: 
        """

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

    def get_student_details(self, reg_no):
        """
        Fetches the students details from the database 
        :param reg_no: The students registration number
        :return: 
        """

        query = "SELECT * FROM student_details WHERE registration_number='{0}'".format(reg_no)
        self.c.execute(query)

        result = self.c.fetchone()
        self.close_db()

        return result

    def get_documents(self, course, year, sem):
        """
        Gets a list of the documents from the database
        :param course: Course the student is taking
        :param year: Current Year
        :param sem: Current Semester
        :return: 
        """

        query = "SELECT * FROM notes WHERE course='{0}' and year={1} and semester={2}".format(course, year, sem)
        self.c.execute(query)

        results = self.c.fetchall()
        self.close_db()

        return results

    def available_hostels(self, gender):
        """
        Checks for available hostel rooms 
        :param gender: 
        :return: 
        """

        query = "SELECT * FROM hostels WHERE gender='{0}' AND available_spaces > 0".format(gender)
        self.c.execute(query)

        results = self.c.fetchall()
        self.close_db()

        return results

    def occupied_hostel(self, hostel_name):
        """
        Reduces hostel spaces by one 
        :param hostel_name: Name of hostel
        :return: 
        """

        query = "UPDATE hostels SET available_spaces=available_spaces-1 WHERE hostel_name='{0}'".format(hostel_name)
        self.c.execute(query)
        self.close_db()

    def assign_hostel(self, hostel_name, registration_number):
        """
        Adds the student to the selected hostel 
        :param hostel_name: Name of hostel
        :param registration_number: Students Registration Number
        :return: 
        """
        query = "UPDATE student_details SET hostel='{0}' WHERE registration_number='{1}'".format(hostel_name,
                                                                                                 registration_number)
        self.c.execute(query)
        self.close_db()

    def add_password_reset_code(self, reset_code, registration_number):
        """
        Adds password reset code to database
        Code will be used to ensure that the correct user is changing the password
        :param reset_code: The code sent to the students email
        :param registration_number: The registration number of the student
        :return: 
        """

        query = "INSERT INTO password_reset (reset_code, registration_number) VALUES('{0}', '{1}')".format(
                    reset_code, registration_number
        )
        self.c.execute(query)
        self.close_db()

    def is_valid_password_reset_link(self, reset_code):
        """
        Confirms whether the password reset code is in the database
        :param reset_code: The reset code the user is attempting to change their password with
        :return: 
        """

        query = "SELECT * FROM password_reset WHERE reset_code='{0}'".format(reset_code)
        self.c.execute(query)
        result = self.c.fetchone()

        query = "DELETE FROM password_reset WHERE reset_code='{0}'".format(reset_code)
        self.c.execute(query)

        self.close_db()

        return result

    def change_password(self, reg_no, new_password):
        """
        Change the users password
        :param reg_no: Student who wants to change their password
        :param new_password: The new password to be used
        :return: 
        """
        new_password = sha512_crypt.encrypt(new_password)

        query = "UPDATE login SET user_password='{0}' WHERE registration_number='{1}'".format(new_password, reg_no)
        self.c.execute(query)

        self.close_db()

    def get_timetable(self, student_details):
        """
        Get the timetable
        :param student_details: Dictionary containing the details of the student
        :return: 
        """

        query = """SELECT timetable.*, units.unit_code, units.unit_lecturer FROM timetable LEFT JOIN units ON 
                    timetable.unit_id=units.unit_id WHERE units.course='{0}' AND  units.year='{1}' AND 
                    units.semester='{2}'""".format(
                        student_details['course'], student_details['current_year'], student_details['current_semester']
        )
        self.c.execute(query)

        results = self.c.fetchall()
        self.close_db()

        return results

    def get_scores(self, registration_number):
        query = "SELECT * FROM scores WHERE registration_number='{0}' ORDER BY score_id".format(registration_number)
        self.c.execute(query)

        scores = self.c.fetchall()
        return scores

    def get_exams(self, student_details):
        """
        Gets the assignments, cats and exam details from the database
        :param student_details: Details of the current student
        :return A list of assignments, cats and exams 
        """

        query = """ SELECT exams.*, units.unit_code, units.unit_lecturer FROM exams LEFT JOIN units ON
                    exams.unit_id=units.unit_id WHERE units.course='{0}' AND  units.year='{1}' AND 
                    units.semester='{2}'""".format(
                        student_details['course'], student_details['current_year'], student_details['current_semester']
        )
        self.c.execute(query)

        results = self.c.fetchall()
        self.close_db()

        return results

    def close_db(self):
        """
        Close the database
        :return: 
        """
        self.c.close()
        self.conn.close()
        gc.collect()
