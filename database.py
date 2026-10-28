"""Модуль для роботи з базою даних SQLite."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"


def get_connection():
    """Створює підключення до бази даних та вмикає підтримку зовнішніх ключів."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Створює необхідні таблиці в базі даних, якщо вони ще не існують."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Таблиця груп
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL UNIQUE
        );
        """)

        # Таблиця студентів
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            student_ticket TEXT NOT NULL UNIQUE,
            group_id INTEGER,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE SET NULL
        );
        """)

        # Таблиця предметів
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL UNIQUE,
            hours INTEGER NOT NULL CHECK(hours > 0)
        );
        """)

        # Таблиця оцінок
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            grade INTEGER NOT NULL CHECK(grade >= 0 AND grade <= 100),
            date_passed TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
        );
        """)

        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Базу даних успішно створено!")