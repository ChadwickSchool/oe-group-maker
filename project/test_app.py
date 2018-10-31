# project/test_basic.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from test_database_setup import Base, Student, engine
import os
import unittest
from application import showStudent, showStudents, newStudent
from application import session, app


app = Flask(__name__)
engine = create_engine('sqlite:///test_database.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################
#     def create_app():
#         app = Flask(application)
#
#         with app.app_context():
#             init_db()
#             setUp()
#             self.assertEqual(app.debug, False)
#             tearDown()
#
#         return app
#
#     def setUp(self):
#         app.config['TESTING'] = True
#         app.config['WTF_CSRF_ENABLED'] = False
#         app.config['DEBUG'] = False
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
#         self.app = app.test_client()
#
# # executed after each test
#     def tearDown(self):
#         pass

    # executed prior to each test



###############
#### tests ####
###############


    def test_showStudent(self):
        expected_results = { "first_name" : "Michael"
                    , "last_name" : "Huang"
                    }
        results = showStudent(1, session)
        self.assertEqual(results, expected_results)

    def test_showStudents(self):
            expected_results = [{ 'first_name' : 'Michael'
                        , 'last_name' : 'Huang'
                        }, { 'first_name' : 'J'
                                    , 'last_name' : 'D'
                                    }]
            results = showStudents(session)
            self.assertEqual(results, expected_results)

    def test_newStudent(self):
        oldDb = showStudents(session)
        new_Student = newStudent('David','Malone', session)
        oldDb.append(new_Student)
        newDb = showStudents(session)
        self.assertEqual(newDb, oldDb)

if __name__ == "__main__":
    unittest.main()