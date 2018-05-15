# coding: utf8

# Copyright 2017 Jacques Berger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sqlite3
from binascii import a2b_base64
import os


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            my_path = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(my_path, 'db/db.db')
            self.connection = sqlite3.connect(path)
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_pictures_imgdata(self, pic_id):
        cursor = self.get_connection().cursor()
        cursor.execute(("SELECT img_data FROM Pictures WHERE pic_id=?"),
                       (pic_id,))
        picture = cursor.fetchone()
        if picture is None:
            return None
        else:
            blob_data = picture[0]
            return blob_data

    def insert_pictures(self, pic_id, file_data):
        listed_img_uri = file_data.split(',')
        img_base64_tostring = listed_img_uri[1]

        # convert string to binary data for writing purpose
        binary_data = a2b_base64(img_base64_tostring)
        connection = self.get_connection()
        connection.execute(
            "INSERT INTO Pictures(pic_id, img_data) VALUES(?, ?)",
            [pic_id, sqlite3.Binary(binary_data)])
        connection.commit()

    def update_pictures(self, pic_id, file_data):
        listed_img_uri = file_data.split(',')
        img_base64_tostring = listed_img_uri[1]

        # convert string to binary data for writing purpose
        binary_data = a2b_base64(img_base64_tostring)
        connection = self.get_connection()
        connection.execute("UPDATE Pictures SET img_data = ? WHERE pic_id = ?",
                           [sqlite3.Binary(binary_data), pic_id])
        connection.commit()

    def get_five_random_animals(self):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute('SELECT * FROM Animal ORDER BY random() LIMIT 5')
        return cursor.fetchall()

    def get_animals_by_date_creation(self, option):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute(" SELECT * FROM Animal WHERE "
                       "strftime('%Y-%m-%d','now') >= strftime"
                       "('%Y-%m-%d',date_creation) ORDER BY "
                       "date_creation DESC")
        if option == 1:
            return self.animal_to_list_of_dict(cursor.fetchall())
        else:
            return cursor.fetchmany(5)

    def get_animals_like_query(self, query, filter):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        query = "%" + query + "%"

        if filter == 'all':
            sql = "SELECT * FROM Animal a WHERE a.name LIKE ? " \
                  "OR a.description LIKE ? OR a.type LIKE ? OR a.race LIKE ?"
            cursor.execute((sql), (query, query, query, query,))
        elif filter == 'other':
            sql = "SELECT * FROM Animal a WHERE  a.type " \
                  "NOT IN ('dog','cat') " \
                  "AND a.name LIKE ? OR a.description LIKE ?"
            cursor.execute((sql), (query, query,))
        elif filter == 'dogs':
            sql = "SELECT * FROM Animal a WHERE  a.type LIKE ? " \
                  "AND a.description LIKE ? OR a.type LIKE ? " \
                  "AND a.name LIKE ? "
            cursor.execute((sql), ('%dog%', query, '%dog%', query,))
        elif filter == 'cats':
            sql = "SELECT * FROM Animal a WHERE  a.type LIKE ? " \
                  "AND a.description LIKE ? OR a.type LIKE ? " \
                  "AND a.name LIKE ? "
            cursor.execute((sql), ('%cat%', query, '%cat%', query,))
        else:
            sql = "SELECT * FROM Animal a WHERE a.name LIKE ? " \
                  "OR a.description LIKE ? OR a.type LIKE ? OR a.race LIKE ?"
            cursor.execute((sql), (query, query, query, query,))

        return cursor.fetchall()

    def get_all_animals(self):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute('SELECT * FROM Animal')
        return cursor.fetchall()

    def get_animal_by_name(self, name):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        sql_query = "%" + name + "%"
        cursor.execute("SELECT * FROM Animal WHERE name LIKE ?", (sql_query,))
        return cursor.fetchone()

    def get_animals_by_id(self, id):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM Animal WHERE id = ?", (id,))
        return cursor.fetchall()

    def get_animals_by_owner_id(self, owner_id):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM Animal WHERE owner_id = ?", (owner_id,))
        return cursor.fetchall()

    def get_animals_id_like(self, id):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        sql_id = "%" + id + "%"
        cursor.execute("SELECT * FROM Animal WHERE id LIKE ?",
                       (sql_id,))
        return cursor.fetchall()

    def get_animal_pic_id_by_owner_id(self, owner_id):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("SELECT pic_id FROM Animal WHERE owner_id = ?",
                       (owner_id,))
        return cursor.fetchall()

    def delete_animal(self, owner_id, pic_id):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM Animal WHERE owner_id=?", (owner_id,))
        connexion.commit()
        cursor.execute("DELETE FROM Pictures WHERE pic_id=?", (pic_id,))
        connexion.commit()

    def update_animal(self, name, type, race, age, date_creation, description,
                      pic_id, owner_id):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        if pic_id == '':
            # no need to update image
            sql_query = "UPDATE Animal " \
                        "SET name=?, type=?, race=?, age=?,"\
                        " date_creation=?, description=? WHERE owner_id=?"
            cursor.execute(sql_query,
                           (name, type, race, age, date_creation, description,
                            owner_id,))
        else:
            sql_query = "UPDATE Animal " \
                        "SET name=?, type=?, race=?, age=?, " \
                        "date_creation=?, description=?, pic_id=? " \
                        "WHERE owner_id=?"
            cursor.execute(sql_query, (name, type, race, age, date_creation,
                                       description, pic_id, owner_id,))
        connexion.commit()
        return cursor.fetchone()

    def insert_animal(self, name, type, race, age, date_creation, description,
                      pic_id, owner_id):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute(
            "INSERT INTO Animal(name, type, race, age, date_creation, "
            "description, pic_id, owner_id) "
            "VALUES(?, ?, ?, ?, ?,?,?, ?)",
            (name, type, race, age, date_creation, description, pic_id,
             owner_id,))
        connexion.commit()

    def create_user(self, username, name, family_name, phone, address, email,
                    salt, hashed_password):
        connection = self.get_connection()
        connection.execute((
                           "INSERT INTO Users(username, name, family_name, "
                           "phone, address, email, salt, hash)"
                           " VALUES(?, ?, ?, ?, ?, ?, ?, ?)"),
                           (username, name, family_name, phone, address, email,
                            salt,
                            hashed_password))
        connection.commit()

    def get_user_id_by_email(self, email):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT id FROM Users WHERE username=?', (email,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0]

    def get_user_hash_by_username(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT salt, hash FROM Users WHERE username=?',
                       (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0], user[1]

    def get_user_info_by_username(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT * FROM Users WHERE username=?', (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0], user[1], user[2], user[3], user[4], user[5], user[
                6]

    def get_user_username_by_email(self, email):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT username FROM Users WHERE email=?', (email,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0]

    def get_user_email_by_animal_id(self, animal_id):
        cursor = self.get_connection().cursor()
        cursor.execute(
            'SELECT email FROM Users u JOIN Animal a ON u.id = a.owner_id '
            'WHERE a.id=?',
            (animal_id,))
        email = cursor.fetchone()
        return email[0]

    def get_user_email_by_username(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT email FROM Users u WHERE u.username=?',
                       (username,))
        email = cursor.fetchone()
        return email[0]

    def get_user_id_by_id_session(self, id_session):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT DISTINCT  u.id '
                       'FROM sessions s JOIN Users u '
                       'ON s.username = u.username '
                       'WHERE id_session=?', (id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def get_user_adresse_by_animal_id(self, animal_id):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT u.address '
                       'FROM Animal a JOIN Users u '
                       'ON u.id = a.owner_id '
                       'WHERE a.id=?', (animal_id,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def get_all_users(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Users')
        return cursor.fetchall()

    def update_user_password(self, id, salt, hash):
        connection = self.get_connection()
        connection.execute('UPDATE Users SET salt=?, hash=? WHERE id=?',
                           (salt, hash, id,))
        connection.commit()

    def update_user(self, id, username, name, family_name, phone, address,
                    email, salt, hash, session_username):
        connection = self.get_connection()
        connection.execute('UPDATE Users '
                           'SET username=?, name=?, family_name=?, phone=?, '
                           'address=?, email=?, salt=?, hash=? '
                           'WHERE id=?',
                           (username, name, family_name, phone, address, email,
                            salt, hash, id,))
        connection.commit()

        # user wants to update his username
        if session_username != username:
            connection.execute('UPDATE sessions '
                               'SET username=?'
                               'WHERE username=?',
                               (username, session_username,))
            connection.commit()

    def save_session(self, id_session, username):
        connection = self.get_connection()
        connection.execute(("INSERT INTO sessions(id_session, username) "
                            "VALUES(?, ?)"), (id_session, username,))
        connection.commit()

    def delete_session(self, id_session):
        connection = self.get_connection()
        connection.execute("DELETE FROM sessions WHERE id_session=?",
                           (id_session,))
        connection.commit()

    def get_session_username_by_id_session(self, id_session):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT username FROM sessions WHERE id_session=?",
                       (id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def get_account_token_by_username(self, username):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT token FROM Account WHERE username=?",
                       (username,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def delete_account_by_username(self, username):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Account WHERE username=?", (username,))
        connection.commit()

    def animal_to_list_of_dict(self, animal):
        list_animal = []
        for row in animal:
            list_animal.append(self.to_dict(row))
        return list_animal

    def create_account(self, username, user_email, token, date):
        connection = self.get_connection()
        connection.execute(
            "INSERT INTO Account(username, email,token,date_sent) "
            "VALUES(?, ?, ?, ?)",
            (username, user_email, token, date))
        connection.commit()

    def to_dict(self, row):
        return {"id": row[0], "titre": row[1], "identifiant": row[2],
                "auteur": row[3], "date_publication": row[4],
                "paragraphe": row[5]}
