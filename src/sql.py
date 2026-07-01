import sqlite3
from pathlib import Path
import datetime
import sys
import click


def ok(msg):
    """Print a success message in green."""
    click.echo(click.style(msg, fg="green"))


def err(msg):
    """Print an error/failure message in red."""
    click.echo(click.style(msg, fg="red"))


def initDB():
    global db, cursor

    # When frozen into an executable (PyInstaller), __file__ points to a temp
    # extraction folder that is wiped on exit, so store the DB next to the
    # executable instead. Otherwise store it next to this source file.
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    db_path = base / "cat-a-log.db"

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
    cursor.execute("PRAGMA foreign_keys = ON")
    db.commit()

def addEntry(name, birth, breed):
    try:
        cursor.execute('''
            INSERT INTO cats (name, birth_date, breed)
            VALUES(?,?,?)
        ''', (name, birth, breed))
        db.commit()
        ok(f"{name} added to database successfully!")
    except sqlite3.IntegrityError:
        err("Entry already exists!")
        return False

def updateEntry(id, column, value):
    allowed = ("name", "birth_date", "breed")
    if column not in allowed:
        err("Invalid column.")
        return False
    try:
        cursor.execute(f'''
            UPDATE cats SET {column} = ? WHERE id = ?
        ''', (value, id))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        err("That cat already exists! Choose a different name.")
        return False
    

def updateLog(id, column, value):
    allowed = ("weight_kg", "activity_level", "appetite", "water_intake", "litter", "notes")
    if column not in allowed:
        err("Invalid column.")
        return False
    cursor.execute(f'''
        UPDATE log SET {column} = ? WHERE id = ?
    ''', (value, id))
    db.commit()
    return True

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
    return cursor.execute('''
        SELECT name, birth_date, breed, created_at, ID FROM cats
    ''').fetchall()

def queryCat(id):
    return cursor.execute('''
        SELECT name, birth_date, breed, created_at, ID FROM cats
        WHERE id = ?
    ''', (id, )).fetchall()

def queryLog(id):
    return cursor.execute('''
        SELECT id, weight_kg, activity_level, appetite, water_intake, litter, notes, created_at, name
        FROM log WHERE id = ?
    ''', (id, )).fetchall()

def metricLog(cat):
    if cat == None:
        return cursor.execute('''
            SELECT id, weight_kg, activity_level, appetite, water_intake, litter, notes, created_at, name
            FROM log
            ''').fetchall()
    else:
        return cursor.execute('''
            SELECT id, weight_kg, activity_level, appetite, water_intake, litter, notes, created_at
            FROM log WHERE name = ?
        ''', (cat, )).fetchall()

def AIfetchLogs(cat_id):
    return cursor.execute('''
        SELECT weight_kg, activity_level, appetite, water_intake, litter, notes
        FROM log WHERE cat_id = ?
    ''', (cat_id,)).fetchall()

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
        err("Select a table")
        return
    db.commit()

def exportLogs(cat):
    if cat is None:
        return cursor.execute('''
            SELECT name, created_at, weight_kg, activity_level, appetite, water_intake, litter, notes
            FROM log
        ''').fetchall()
    else:
        return cursor.execute('''
            SELECT name, created_at, weight_kg, activity_level, appetite, water_intake, litter, notes
            FROM log WHERE name = ?
        ''', (cat, )).fetchall()
    
def catStatus():
    return cursor.execute('''
        SELECT c.name, c.breed, MAX(l.created_at)
        FROM cats c
        LEFT JOIN log l ON c.id = l.cat_id
        GROUP BY c.id
        ORDER BY c.name
    ''').fetchall()

def weightHistory(cat_id):
    return cursor.execute('''
        SELECT weight_kg, created_at FROM log
        WHERE cat_id = ? AND weight_kg IS NOT NULL
        ORDER BY created_at ASC
    ''', (cat_id, )).fetchall()