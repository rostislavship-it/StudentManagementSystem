"""Модуль об'єктних моделей предметної області."""


class Group:
    def __init__(self, group_id: int, group_name: str):
        self.id = group_id
        self.group_name = group_name


class Student:
    def __init__(
        self,
        student_id: int,
        first_name: str,
        last_name: str,
        student_ticket: str,
        group_id: int = None,
    ):
        self.id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.student_ticket = student_ticket
        self.group_id = group_id

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name}"


class Subject:
    def __init__(self, subject_id: int, subject_name: str, hours: int):
        self.id = subject_id
        self.subject_name = subject_name
        self.hours = hours


class Grade:
    def __init__(
        self,
        grade_id: int,
        student_id: int,
        subject_id: int,
        grade: int,
        date_passed: str,
    ):
        self.id = grade_id
        self.student_id = student_id
        self.subject_id = subject_id
        self.grade = grade
        self.date_passed = date_passed