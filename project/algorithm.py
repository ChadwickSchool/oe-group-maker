import flask
from flask import Flask, request
from server.dao import Customer, engine
from sqlalchemy.orm import sessionmaker

def getStudents():
    students = query.all()
    return students
