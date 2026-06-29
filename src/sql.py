import sqlite3
from pathlib import Path
import datetime


def initDB():
    global db, cursor

    db_path = Path(__file__).with_name('cat-a-log.db')
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS cats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            birth_date TEXT,
            breed TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
        
        CREATE TABLE IF NOT EXISTS log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            name TEXT,
            weight_kg REAL,
            activity_level INTEGER,
            appetite TEXT CHECK(appetite IN ("None", "Normal", "Low", "High", "N/A")),
            water_intake TEXT CHECK(water_intake IN ("None", "Normal", "Low", "High", "N/A")),
            litter TEXT CHECK(litter IN ("Normal", "Straining", "Diarrhea", "Constipated", "N/A")),
            notes TEXT,
            FOREIGN KEY (cat_id) REFERENCES cats(id) ON DELETE CASCADE
        );

    ''')
    db.commit()

def addEntry(name, birth, breed):
    try:
        cursor.execute('''
            INSERT INTO cats (name, birth_date, breed)
            VALUES(?,?,?)
        ''', (name, birth, breed))
        db.commit()
        print(f"{name} added to database successfuly!")
    except sqlite3.IntegrityError:
        print("Entry already exists!")
        return False

def log(id, cat, weight, active, appetite, water, litter, notes):
    cursor.execute('''
        INSERT INTO log (cat_id, name, weight_kg, activity_level, appetite, water_intake, litter, notes)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (id, cat, weight, active, appetite, water, litter, notes))
    db.commit()

def fetchCat(name):
    id = cursor.execute('''
        SELECT id FROM cats WHERE name = ?
    ''', (name,)).fetchone()
    try:
        return id[0]
    except TypeError:
        return "NoName"

def listCats():
    cats = cursor.execute('''
        SELECT name, birth_date, breed, created_at FROM cats
    ''').fetchall()
    return cats

def metricLog(cat):
    if cat == None:
        log = cursor.execute('''
            SELECT id, weight_kg, activity_level, appetite, water_intake, litter, notes, created_at, name
            FROM log
            ''').fetchall()
        return log
    else:
        log = cursor.execute('''
            SELECT id, weight_kg, activity_level, appetite, water_intake, litter, notes, created_at
            FROM log WHERE name = ?
        ''', (cat, )).fetchall()
        return log

def fetchLogs(cat_id):
    logs = cursor.execute('''
        SELECT weight_kg, activity_level, appetite, water_intake, litter, notes
        FROM log WHERE cat_id = ?
    ''', (cat_id,)).fetchall()
    return logs

def delete(table, id):
    if table == "cats":
        cursor.execute('''
            DELETE FROM cats
            WHERE id = ?
        ''', (id, ))
    elif table == "log":
        cursor.execute('''
            DELETE FROM log
            WHERE id = ?
        ''', (id, ))
    else:
        print("Select a table")
        return
    db.commit()