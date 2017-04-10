import datetime
import gc

import MySQLdb
from passlib.hash import sha512_crypt


def connection(database):
    conn = MySQLdb.connect(host="localhost", user="developer", passwd="secret", db=database)
    c = conn.cursor(MySQLdb.cursors.DictCursor)

    return c, conn


def user_exists(attempted_reg_no, c, conn):
    query = "SELECT * FROM login WHERE registration_number = '{0}'".format(attempted_reg_no)
    c.execute(query)

    result = c.fetchone()
    close_db(c, conn)

    return True if result else False


def confirm_account(attempted_reg_no, attempted_password, c, conn):
    query = "SELECT * FROM login WHERE registration_number = '{0}'".format(attempted_reg_no)
    c.execute(query)

    result = c.fetchone()
    close_db(c, conn)

    if not result:
        return False

    if sha512_crypt.verify(attempted_password, result['user_password']):
        return True

    else:
        return False


def add_account(details, c, conn):
    query = """INSERT INTO student_details (registration_number, first_name, last_name, other_names, mode_of_admission,
                faculty, course_level, course, email, phone_number, gender, date_of_birth, registration_date, 
                current_year, current_semester, disabled) 
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', 
                '{13}', '{14}', '{15}')
            """.format(
                details.get('registration_number'), details.get('first_name'), details.get('last_name'),
                details.get('other_names'), details.get('mode_of_admission'), details.get('level'),
                details.get('faculty'), details.get('course'), details.get('email'), details.get('phone_number'),
                details.get('gender'), details.get('dob'), datetime.datetime.now(), 1, 1,
                1)

    c.execute(query)
    conn.commit()

    # This is the default password given to all users
    user_password = "password"

    # Encrypt the password
    user_password = sha512_crypt.encrypt(user_password)

    query = """INSERT INTO login (registration_number, email, user_password) VALUES ('{0}', '{1}', '{2}')""".format(
                details['registration_number'], details['email'], user_password
            )

    c.execute(query)
    conn.commit()
    close_db(c, conn)


def get_student_details(reg_no, c, conn):
    query = "SELECT * FROM student_details WHERE registration_number='{0}'".format(reg_no)
    c.execute(query)

    result = c.fetchone()
    close_db(c, conn)

    return result


def get_documents(course, year, sem, c, conn):
    query = "SELECT * FROM notes WHERE course='{0}' and year={1} and semester={2}".format(course, year, sem)
    c.execute(query)

    results = c.fetchall()
    close_db(c, conn)

    return results


def available_hostels(gender, c, conn):
    query = "SELECT * FROM hostels WHERE gender='{0}' AND available_spaces > 0".format(gender)
    c.execute(query)

    results = c.fetchall()
    close_db(c, conn)

    return results


def occupied_hostel(hostel_name, c, conn):
    query = "UPDATE hostels SET available_spaces=available_spaces-1 WHERE hostel_name='{0}'".format(hostel_name)
    c.execute(query)
    close_db(c, conn)


def assign_hostel(hostel_name, registration_number, c, conn):
    query = "UPDATE student_details SET hostel='{0}' WHERE registration_number='{1}'".format(hostel_name,
                                                                                             registration_number)
    c.execute(query)
    close_db(c, conn)


def add_password_reset_code(reset_code, registration_number, c, conn):
    query = "INSERT INTO password_reset (reset_code, registration_number) VALUES('{0}', '{1}')".format(
                reset_code, registration_number
    )
    c.execute(query)
    close_db(c, conn)


def is_valid_password_reset_link(reset_code, c, conn):
    query = "SELECT * FROM password_reset WHERE reset_code='{0}'".format(reset_code)
    c.execute(query)
    result = c.fetchone()

    query = "DELETE FROM password_reset WHERE reset_code='{0}'".format(reset_code)
    c.execute(query)

    close_db(c, conn)

    return result


def change_password(reg_no, new_password, c, conn):
    new_password = sha512_crypt.encrypt(new_password)

    query = "UPDATE login SET user_password='{0}' WHERE registration_number='{1}'".format(new_password, reg_no)
    c.execute(query)

    close_db(c, conn)


def close_db(c, conn):
    c.close()
    conn.close()
    gc.collect()
