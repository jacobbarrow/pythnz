import sqlite3
import random
import string
import config

db = sqlite3.connect('../db.sqlite')
cursor = db.cursor()

# Creates the users table if there's not one already
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
            id TEXT PRIMARY KEY,
            name TEXT,
            password TEXT,
            highest_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0)
''')
db.commit()


def create(name, password):
    # Create a random string w/32 chars
    id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) 
    
    cursor.execute('INSERT INTO users (id, name, password) VALUES (?,?,?)', (id, name, password))
    db.commit()

def findAll():
    cursor.execute('SELECT * FROM users')
    return cursor.fetchall()

def findById(uid):
    cursor.execute('SELECT * FROM users WHERE id=\'{0}\''.format(uid))
    return cursor.fetchone()

def findByName(name):
    cursor.execute('SELECT * FROM users WHERE name=\'{0}\''.format(name))
    return cursor.fetchone()

def incrementTotalScore(uid, amount):
    cursor.execute('UPDATE users SET total_score = total_score + {0} WHERE id=\'{1}\''.format(amount, uid))
    db.commit()

def setHighestScore(uid, new_highest_score):
    cursor.execute('UPDATE users SET highest_score = {0} WHERE id=\'{1}\''.format(new_highest_score, uid))
    db.commit()

