"""Сервісний модуль для бізнес-логіки та опрацювання даних."""

from database import get_connection

# --- РОБОТА З ГРУПАМИ ---

def add_group(group_name: str):
    """Додає нову групу."""
    with get_connection() as conn:
        conn.execute("INSERT INTO groups (group_name) VALUES (?)", (group_name,))

def get_all_groups():
    """Повертає список усіх груп."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, group_name FROM groups ORDER BY group_name;")
        return cursor.fetchall()

# --- РОБОТА З ДИСЦИПЛІНАМИ ---

def add_subject(subject_name: str, hours: int):
    """Додає новий предмет."""
    with get_connection() as conn:
        conn.execute("INSERT INTO subjects (subject_name, hours) VALUES (?, ?)", (subject_name, hours))

def get_all_subjects():
    """Повертає список усіх предметів."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject_name, hours FROM subjects ORDER BY subject_name;")
        return cursor.fetchall()

# --- РОБОТА ЗІ СТУДЕНТАМИ ---

def add_student(first_name: str, last_name: str, student_ticket: str, group_id: int = None):
    """Додає нового студента."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO students (first_name, last_name, student_ticket, group_id)
               VALUES (?, ?, ?, ?)""",
            (first_name, last_name, student_ticket, group_id),
        )

def update_student(student_id: int, first_name: str, last_name: str, student_ticket: str, group_id: int = None):
    """Оновлює дані існуючого студента."""
    with get_connection() as conn:
        conn.execute(
            """UPDATE students 
               SET first_name = ?, last_name = ?, student_ticket = ?, group_id = ?
               WHERE id = ?""",
            (first_name, last_name, student_ticket, group_id, student_id),
        )

def get_all_students_with_info(search_query: str = "", group_filter_id: int = None, sort_order: str = "name_asc"):
    """Повертає список студентів з можливістю сортування за балом та прізвищем."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                s.id, 
                s.last_name || ' ' || s.first_name AS name, 
                s.student_ticket, 
                COALESCE(g.group_name, 'Без групи') AS group_name,
                COALESCE(ROUND(AVG(gr.grade), 1), 0.0) AS avg_grade,
                s.first_name,
                s.last_name,
                s.group_id
            FROM students s
            LEFT JOIN groups g ON s.group_id = g.id
            LEFT JOIN grades gr ON s.id = gr.student_id
            WHERE (s.last_name LIKE ? OR s.first_name LIKE ? OR s.student_ticket LIKE ?)
        """
        params = [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"]

        if group_filter_id is not None:
            query += " AND s.group_id = ?"
            params.append(group_filter_id)

        query += " GROUP BY s.id"

        # Сортування за балом або прізвищем
        if sort_order == "grade_desc":
            query += " ORDER BY avg_grade DESC, s.last_name ASC;"
        elif sort_order == "grade_asc":
            query += " ORDER BY avg_grade ASC, s.last_name ASC;"
        else:
            query += " ORDER BY s.last_name ASC;"

        cursor.execute(query, params)
        return cursor.fetchall()

def delete_student(student_id: int):
    """Видаляє студента за його ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))

# --- РОБОТА З ОЦІНКАМИ ---

def add_grade(student_id: int, subject_id: int, grade: int, date_passed: str):
    """Виставляє оцінку студенту."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO grades (student_id, subject_id, grade, date_passed)
               VALUES (?, ?, ?, ?)""",
            (student_id, subject_id, grade, date_passed)
        )