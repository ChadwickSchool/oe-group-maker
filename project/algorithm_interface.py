import flask
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Student, engine, Preference
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from Student_class import Student_class

app = Flask(__name__)
engine = create_engine('sqlite:///database.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

'''
selects students from grade level
'''
# def getstudents_by_gradelevel(gradeLevel):
#     return session.query(Student).filter_by(grade=gradeLevel).all()

'''
selects students from trip ID
'''
# def getstudents_by_tripID(tripID):
#     return session.query(Student).filter_by(id = tripID).all()

# def getpreferences_by_studentID(studID):
#     return session.query(Preference).filter_by(id = studID).all()

'''
finds tentative parteners for each person using student ID
'''
def temp_partner_id_db(student, stuID):
    student.partner = session.query(Preference).filter_by(student_id = stuID).filter_by(priority = 1).one().name
    #student.partner = student.preferences[0]
    return student.partner

'''
finds tentative parteners for each person using student preference list
'''
def temp_partner_id(student):
    student.partner = student.preferences[student.preference_index]
    student.preference_index = student.preference_index + 1
    return student.partner

'''
finds tentative parteners for each person using student last name
'''
def temp_partner_last_name(student, stuLN):
    student.partner = session.query(Preference).filter_by(last_name = stuLN).one().name
    return student.partner

'''
eliminates partners given a preference string
'''
# def remove_one_student(student, preference):
#     student.remove_preference_string(preference)

'''
eliminates students in a lower preference rating compared to the given
'''
# def remove_lesser_students(student, preference):
#     time_to_delete = False
#     for x in student.preferences:
#         if time_to_delete == True:
#             student.remove_preference_string(preference)
#         if preference == student.prefernces[x]:
#             time_to_delete = True
#
# def setup(num):
#     for x in range(num):
#         students.append(Student())

'''
deletes preferences lower than the "most preferred"... step 2 of the irving algorithm
'''
def remove_lowpriority_pairs(student, session):
#find first preference (student y) of given student (student x)
    # preferences = session.query(Preference).filter_by(student_id = student.id).all()
    preferences = session.query(Preference).filter_by(priority = 3)
    #print(preferences)
    first_priority = preferences.filter_by(student_id = student.id).one()
    student_to_keep = session.query(Student).filter_by(first_name = first_priority.name).one()
    print("\n")
    print("student to keep")
    print(student_to_keep.first_name)
    print("student to keep prefs")
    student_tkPrefs = session.query(Preference).filter_by(student_id = student_to_keep.id).all()
    for stud in student_tkPrefs:
        print(stud.name)
    student_tk = Student_class(student_tkPrefs, student_to_keep.first_name, student_to_keep.last_name)
#find student x in student y's preference list
    x = 0
    for stud in student_tk.preferences:
        x += 1
        if student.first_name == stud.name:
            print("delete preferences afte r: " + stud.name)
            while(x < 3):
                k = abs(x-3)
                preference_to_del = session.query(Preference).filter_by(student_id = student_to_keep.id)
                if preference_to_del.filter_by(priority = k).one_or_none() is not None:
                    preference = preference_to_del.filter_by(priority = k).one()
                    print("preference(s) to delete: " + preference.name)
                    print("deleting: " + preference.name + " from: ")
                    print(preference.student_id)
                    session.delete(preference)
                    id_pref_to_del = preference.id
                    name_of_pref = preference.name
#remove students (z) in student y's preference list that have lower priority than student x
#remove student y from students z's lists
                    student_tbr = session.query(Student).filter_by(first_name = name_of_pref).one()
                    student_remove = Student_class(session.query(Preference).filter_by(student_id = student_tbr.id).all(), student_tbr.first_name, student_tbr.last_name)
                    for stud in student_remove.preferences:
                        if stud.name == student_to_keep.first_name:
                            studs_to_del = session.query(Preference).filter_by(name = student_to_keep.first_name)
                            if studs_to_del.filter_by(student_id = student_tbr.id).one_or_none() is not None:
                                studs_to_del = studs_to_del.filter_by(student_id = student_tbr.id).one()
                                print("deleting: " + studs_to_del.name + " from ")
                                print(studs_to_del.student_id)
                                session.delete(studs_to_del)
                                session.commit()
                x+=1

#input student is student x
#first_priority is same student as student_to_keep and student_tk (student y)
#student_to_be_removed is same student as student_tbr and student_remove (student z)

# def cycle_finder(students):
#     i = 0;
#     while True:
#         p.append(students[i])
#         q.append(students[i].preferences[-1])
#         i += 1
#
def check_for_mutual_pref(student, session):
    preferences = session.query(Preference).filter_by(student_id = student.id).all()
    students_to_remove = []
    if len(preferences) > 2:
        k = 0
        for pref in preferences:
            x = 0
            student_mutual = session.query(Student).filter_by(first_name = pref.name).one()
            mutual_prefs = session.query(Preference).filter_by(student_id = student_mutual.id).all()
            for pref in mutual_prefs:
                if student_mutual.first_name == student.first_name:
                    x += 1
                    k += 1
            if x == 0:
                student_to_remove = session.query(Preference).filter_by(name = student_mutual.first_name)
                student_to_remove = student_to_remove.filter_by(student_id = student.id).one()
                students_to_remove.append(student_to_remove)
        if k > 0:
            for pref in students_to_remove:
                session.delete(pref)
                session.commit()
        if k == 0:
            last_pref_remove = session.query(Preference).filter_by(priority = 1)
            l_p_r = last_pref_remove.filter_by(student_id = student.id).one()
            session.delete(l_p_r)
            session.commit()




'''
exports the final list (currently returns doubles, this is a bad thing and will be fixed)
'''
def export_list(students):
    list = []
    for x in students:
        list.append(x.partner.name)

    return list

sp1 = ["Bob", "Joe", "Fred"]
sp2 = session.query(Preference).filter_by(student_id = 2).all()
sp3 = []
for i in sp2:
    sp3.append(i.name)
s1 = Student_class(sp3, "Ryan", "Hom")
print(temp_partner_id(s1))

print(sp3)

'''
Janky first step in the alg. Will put into a method
'''
print("IT'S GETTING REAL NOW")
students = []
temp1 = session.query(Student).all()
temp2 = None
temp3 = []
count = 1;
#makes a list of Student objects from the database
for i in temp1:
    temp2 = session.query(Preference).filter_by(student_id = count).all()
    for x in temp2:
        temp3.append(x.name)
    students.append(Student_class(temp2, i.first_name, i.last_name))
    count = count + 1
same = 0
while same < 4:
    for i in students:
        if(i.partner == ""):
            print(temp_partner_id(i).name)
        for x in students:
            if(i.partner == x.partner):
                for y in students:
                    if(i.partner == y):
                        for a in range(len(y.preferences), 0, -1):
                            if(a.preferences[a].name == i.first_name):
                                print(temp_partner_id(i))
                                i.remove_preference_string(a.preferences[a].name)
                            elif(a.preferences[a].name == x.first_name):
                                print(temp_partner_id(x))
                                x.remove_preference_string(a.preferences[a].name)
    same += 1

print(export_list(students))
