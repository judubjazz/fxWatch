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
from decimal import Decimal, getcontext
import datetime

class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d

            my_path = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(my_path, 'db/db.db')
            self.connection = sqlite3.connect(path)
            self.connection.row_factory = dict_factory
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_rates(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM Rates")
        rates = cursor.fetchall()
        if not rates:
            return None
        else:
            return rates

    def get_rates_like(self, symbol):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM Rates WHERE symbol LIKE ?", [symbol])
        rates = cursor.fetchall()
        if not rates:
            return None
        else:
            return rates

    def insert_rates(self, rates):
        connection = self.get_connection()
        for rate in rates:
            if rate['symbol'] == 'EURCAD':
                connection.execute("INSERT INTO Eurcad (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'EURUSD':
                connection.execute("INSERT INTO Eurusd (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'EURAUD':
                connection.execute("INSERT INTO Euraud (bid, ask, average, delta,  date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'EURCHF':
                connection.execute("INSERT INTO Eurchf (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'AUDCAD':
                connection.execute("INSERT INTO Audcad (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'AUDUSD':
                connection.execute("INSERT INTO Audusd (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'AUDCHF':
                connection.execute("INSERT INTO Audchf (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'USDCHF':
                connection.execute("INSERT INTO Usdchf (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'USDCAD':
                connection.execute("INSERT INTO Usdcad (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            elif rate['symbol'] == 'CADCHF':
                connection.execute("INSERT INTO Cadchf (bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?)",
                                   [rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
            connection.execute("INSERT INTO Rates (symbol, bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?, ?)",
                               [rate['symbol'], rate['bid'], rate['ask'], rate['average'], rate['delta'], rate['date_created']])
        connection.commit()

    def insert_rate(self, rate):
        connection = self.get_connection()
        print(str(rate['delta']))
        connection.execute("INSERT INTO Rates (symbol, bid, ask, average, delta, date_created) VALUES(?, ?, ?, ?, ?, ?)",
                           [rate['symbol'], rate['bid'], rate['ask'], rate['average'], str(rate['delta']), rate['date_created']])
        connection.commit()

    def update_rate(self, rate):
        bid = rate['bid']
        ask = rate['ask']
        average = (float(bid) + float(ask)) / 2
        getcontext().prec = 8
        delta = Decimal(bid) - Decimal(ask)
        connection = self.get_connection()
        connection.execute("UPDATE Rates SET bid = ?, ask = ?, average = ?, delta = ? WHERE symbol LIKE ?",
                           [bid, ask, average, str(delta), rate['symbol']])
        connection.commit()

    def update_daily_rates(self, dayID, rate, date_created):
        data = str(rate)
        connection = self.get_connection()
        connection.execute("UPDATE DailyRates SET data = ?, date_created = ? WHERE id = ?", [data, date_created, dayID])
        connection.commit()

    def get_daily_rates(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM  DailyRates ORDER BY date_created DESC")
        return cursor.fetchall()

    def get_daily_rate_by_id(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM  DailyRates WHERE id = ?", [id])
        return cursor.fetchone()

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
        cursor.execute(" SELECT * FROM Animal WHERE strftime('%Y-%m-%d','now') >= strftime ('%Y-%m-%d',date_creation) ORDER BY date_creation DESC")
        if option == 1:
            return self.animal_to_list_of_dict(cursor.fetchall())
        else:
            return cursor.fetchmany(5)

    def get_animal_by_name(self, name):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        sql_query = "%" + name + "%"
        cursor.execute("SELECT * FROM Animal WHERE name LIKE ?", (sql_query,))
        return cursor.fetchone()

    def create_user(self, username, email, salt, hashed_password):
        connection = self.get_connection()
        connection.execute((
            "INSERT INTO Users(username, email, salt, hash) VALUES(?, ?, ?, ?)"),(username, email, salt, hashed_password))
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
        cursor.execute('SELECT salt, hash FROM Users WHERE username=?',[username])
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user['salt'], user['hash']

    def get_user_info_by_username(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT * FROM Users WHERE username=?', (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user['id'], user['username'], user['email'], user['salt'], user['hash']

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

    def update_user(self, id, username, email, salt, hash, session_username):
        connection = self.get_connection()
        connection.execute('UPDATE Users '
                           'SET username=?, email=?, salt=?, hash=? '
                           'WHERE id=?',
                           (username, email,salt, hash, id,))
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
        cursor.execute("SELECT username FROM sessions WHERE id_session=?",(id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data['username']

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

    def to_dict(self, row):
        return {"id": row[0], "titre": row[1], "identifiant": row[2],"auteur": row[3], "date_publication": row[4], "paragraphe": row[5]}
