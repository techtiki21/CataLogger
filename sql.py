import sqlite3
from pathlib import Path
import datetime

db = None
cursor = None

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
            weight_kg REAL,
            activity_level INTEGER,
            appetite TEXT CHECK(appetite IN ('None', 'Normal', 'Low', 'High')),
            water_intake TEXT CHECK(water_intake IN ('Normal', 'Decreased', 'Increased')),
            litter_box TEXT CHECK(litter_box IN ('Normal', 'Straining', 'Diarrhea', 'Constipated')),
            notes TEXT,
            FOREIGN KEY (cat_id) REFERENCES cats(id) ON DELETE CASCADE
        );

    ''')
    db.commit()

def addEntry(name, birth, breed):
    cursor.execute('''
        INSERT INTO cats (name, birth_date, breed)
        VALUES(?,?,?)
    ''', (name, birth, breed))
    db.commit()