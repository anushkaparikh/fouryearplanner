import os
import csv
import datetime
import xml.dom.minidom
#pip install requests
import requests
#pip install urllib3
import urllib3
# mongodb stuff
import pymongo
import json
from pymongo import MongoClient

from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)

db = SQLAlchemy(app)

# mongo stuff
mdb = cluster["fouryearplan"]
collection = mdb["prereq"] # access to the collection
collection2 = mdb["tracks"]
collection3 = mdb["credits"]
collection4 = mdb["planned"]
collection5 = mdb["coursetracks"]
collection6 = mdb["users"]

courses_planned = []
courses_taken = []
courses_tracks = []
netid = None


# class test(db.Model):
#     _id = db.Column(db.Integer, primary_key=True)
#     major = db.Column(db.String(255))
#     interests = db.Column(db.String(255))

#     def __init__(self, major, interests):
#         self.major = major
#         self.interests = interests

class custom_courses(db.Model):
    department = db.Column(db.String(64), primary_key=True)
    number = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(64))
    credit = db.Column(db.String(64))

    def __init__(self, department, number, name, credit):
        self.department = department
        self.number = number
        self.name = name
        self.credit = credit

class user(db.Model):
    netid = db.Column(db.String(10), primary_key=True)
    major = db.Column(db.String(64))
    track_name = db.Column(db.String(64), db.ForeignKey('tracks.track_name'))

    def __init__(self, netid, major, track_name):
        self.netid = netid
        self.major = major 
        self.track_name = track_name

class tracks(db.Model):
    track_name = db.Column(db.String(64), primary_key=True)
    department = db.Column(db.String(64))
    major = db.Column(db.String(64))

    def __init__(self, track_name, department, major):
        self.track_name = track_name
        self.department = department 
        self.major = major

@app.route("/", methods=['GET', 'POST'])
def index():
    global courses_planned
    global courses_taken
    global netid
    global courses_tracks
    if request.method == "POST":
        if 'init_info_form' in request.form:
            netid = request.form['netid']
            major = request.form['major']
            interests = request.form['interests']

            # Load user courses if already exists, else create new schedule based off data
            x = collection6.find({"_id": netid}).count()
            if x != 0:
                user = collection6.find_one({"_id": netid})
                courses_planned = user['course_list']
                courses_taken = user['taken_list']
            else:
                courses_planned = (collection4.find_one(major))['course_planned']
                courses_taken = []

            if interests != "No Track":
                courses_tracks = (collection5.find_one(interests))['sub']
            if (request.form.get('chem102') == "on" and "CHEM 102" not in courses_taken):
                courses_taken.append("CHEM 102")
            if (request.form.get('chem103') == "on" and "CHEM 103" not in courses_taken):
                courses_taken.append("CHEM 103")
            if (request.form.get('math221') == "on" and "MATH 221" not in courses_taken):
                courses_taken.append("MATH 221")
            if (request.form.get('math231') == "on" and "MATH 231" not in courses_taken):
                courses_taken.append("MATH 231")
            if (request.form.get('math241') == "on" and "MATH 241" not in courses_taken):
                courses_taken.append("MATH 241")
            if (request.form.get('math415') == "on" and "MATH 415" not in courses_taken):
                courses_taken.append("MATH 415")
            if (request.form.get('phys211') == "on" and "PHYS 211" not in courses_taken):
                courses_taken.append("PHYS 211")
            if (request.form.get('phys212') == "on" and "PHYS 212" not in courses_taken):
                courses_taken.append("PHYS 212")
            if (request.form.get('math286') == "on" and "MATH 286" not in courses_taken):
                courses_taken.append("MATH 286")
            if (request.form.get('rhet105') == "on" and "RHET 105" not in courses_taken):
                courses_taken.append("RHET 105")
            
            for c in courses_taken:
                for sem in courses_planned:
                    if c in sem:
                        sem.remove(c)

            # Insert into SQL database
            db.session.execute('INSERT INTO user(netid, major, track_name) VALUES(:netid, :major, :interests) ON DUPLICATE KEY UPDATE major=VALUES(major), track_name=VALUES(track_name)',{'netid':netid, 'major':major, 'interests':interests})
            db.session.commit()

        return render_template("drag.html", prereq={}, credits_array={}, courses_planned=courses_planned, courses_taken=courses_taken, track_courses=courses_tracks)

    tracks = {}
    for t in collection2.find():
        major = t.get('_id')
        tracks[major] = t.get('track')

    return render_template("index.html", tracks=tracks, courses_planned=courses_planned, courses_taken=courses_taken)

@app.route("/planner", methods=['GET', 'POST'])
def planner():
    prereq = {}
    credits_array = {}
    global courses_planned
    global courses_taken
    if request.method == "POST":
        if 'insert_form' in request.form:
            classDept = request.form['department']
            classDept = classDept.upper()
            classNum = request.form['number']
            className = request.form['name']
            classCredit = request.form['credit']

            # course = custom_courses(classCRN, className, classType, classDept, classCredit, classDay, classTime, classProf, classLoc)
            # db.session.add(course)

            db.session.execute('INSERT INTO custom_courses(department, number, name, credit) VALUES(:classDept, :classNum, :className, :classCredit) ON DUPLICATE KEY UPDATE name=VALUES(name), credit=VALUES(credit)',{'classDept':classDept,'classNum':classNum,'className':className,'classCredit':classCredit})

            db.session.commit()

        elif 'delete_form' in request.form:
            classDept = request.form['department']
            classNum = request.form['number']
            
            found_course = custom_courses.query.filter_by(department=classDept, number=classNum)
            for course in found_course:
                # db.session.delete(course)
                db.session.execute('DELETE FROM custom_courses WHERE department=:classDept AND number=:classNum',{'classDept':classDept, 'classNum':classNum})
            
            db.session.commit()

        elif 'update_form' in request.form:
            classDept = request.form['department']
            classNum = request.form['number']
            classLabel = request.form['label']
            classVal = request.form['val'] 

            found_course = custom_courses.query.filter_by(department=classDept, number=classNum)
            
            if classLabel == "name":
                # found_course.update({'type':classVal})
                db.session.execute('UPDATE custom_courses SET name=:classVal WHERE department=:classDept AND number=:classNum',{'classVal':classVal,'classDept':classDept,'classNum':classNum})
            elif classLabel == "credit":
                # found_course.update({'department':classVal}) 
                db.session.execute('UPDATE custom_courses SET credit=:classVal WHERE department=:classDept AND number=:classNum',{'classVal':classVal,'classDept':classDept,'classNum':classNum})

            db.session.commit()

        elif 'search_form' in request.form:
            resultType = request.form.get('resultType')
            searchDept = request.form.get('department')
            searchNum = request.form.get('number')
            searchName = request.form.get('name')
            searchCredit = request.form.get('credit')

            stringDept = "%{}%".format(searchDept)
            stringNum = "%{}%".format(searchNum)
            stringName = "%{}%".format(searchName)
            stringCredit = "%{}%".format(searchCredit)

            search_params = []
            if searchDept:
                search_params.append(custom_courses.department.like(stringDept))
            if searchNum:
                search_params.append(custom_courses.number.like(stringNum))
            if searchName:
                search_params.append(custom_courses.name.like(stringName))
            if searchCredit:
                search_params.append(custom_courses.credit.like(stringCredit))

            if resultType == "AND":
                # courses = custom_courses.query.filter(custom_courses.crn.like(stringCRN), custom_courses.name.like(stringName), custom_courses.types.like(stringType), custom_courses.department.like(stringDept), custom_courses.credit.like(stringCredit), custom_courses.days.like(stringDay), custom_courses.time.like(stringTime), custom_courses.professor.like(stringProf)).all()
                courses = db.session.execute('SELECT * FROM custom_courses WHERE \
                                            department LIKE :stringDept AND \
                                            number LIKE :stringNum AND \
                                            name LIKE :stringName AND \
                                            credit LIKE :stringCredit',
                                            {'stringDept':stringDept,'stringNum':stringNum,'stringName':stringName,'stringCredit':stringCredit})
            if resultType == "OR":
                if len(search_params) == 0:
                    courses = db.session.execute('SELECT * FROM custom_courses')
                else:
                    courses = db.session.query(custom_courses).filter(or_(*search_params)).all()
            

            # CS 225","prereq":[ ["CS 125", "ECE 220"],["MATH 213", "MATH 347", "MATH 412", "MATH 413"] ]
            # {CS225: [ ["CS 125", "ECE 220"],["MATH 213", "MATH 347", "MATH 412", "MATH 413"] ], ECE220: [[]]}
            # Output of find: {'_id': 'CS 225', 'prereq': [['CS 125', 'ECE 220'], ['MATH 213', 'MATH 347', 'MATH 412', 'MATH 413']]}
            # c = collection.find_one("CS 225")
            # {'_id': 'CS 225', 'prereq': [['CS 125', 'ECE 220'], ['MATH 213', 'MATH 347', 'MATH 412', 'MATH 413']]}

            # for c in collection.find():
            # print(collection.find_one(c.get('_id')))
            # Output of above 
            # {'_id': 'CS 225', 'prereq': [['CS 125', 'ECE 220'], ['MATH 213', 'MATH 347', 'MATH 412', 'MATH 413']]}
            # {'_id': 'ECE 220', 'prereq': ['ECE 120']}           

            for c in collection.find():
                course_id = c.get('_id')
                prereq[course_id] = c.get('prereq')

            for c in collection3.find():
                course_id = c.get('_id')
                credits_array[course_id] = c.get('credit')

            courses_planned = request.form.get("courses_schedule_search")
            courses_planned = json.loads(courses_planned)

            courses_taken = request.form.get("credit_courses_search")
            courses_taken = json.loads(courses_taken)

            return render_template("drag.html", courses=courses, prereq=prereq, credits_array=credits_array, courses_planned=courses_planned, courses_taken=courses_taken, track_courses=courses_tracks)
        
        elif 'save' in request.form:
            for c in collection.find():
                course_id = c.get('_id')
                prereq[course_id] = c.get('prereq')

            for c in collection3.find():
                course_id = c.get('_id')
                credits_array[course_id] = c.get('credit')

            courses_planned = request.form.get("courses_schedule_save")
            courses_planned = json.loads(courses_planned)

            courses_taken = request.form.get("credit_courses_save")
            courses_taken = json.loads(courses_taken)

            # MongoDB
            x = collection6.find({"_id": netid}).count()
            if x == 0:
                postuser = {"_id": netid, "course_list": courses_planned, "taken_list": courses_taken}
                collection6.insert_one(postuser)
            else:
                myquery = { "_id": netid }
                newvalues = { "$set": { "course_list": courses_planned, "taken_list": courses_taken} }
                collection6.update_one(myquery, newvalues)


        return render_template("drag.html", prereq=prereq, credits_array=credits_array, courses_planned=courses_planned, courses_taken=courses_taken, track_courses=courses_tracks)
    else:
        # return render_template("drag.html", prereq=prereq, credits_array=credits_array, courses_planned=courses_planned, courses_taken=courses_taken)
        return redirect(url_for('index'))

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/results", methods=['POST', 'GET'])
def results():
    resultType = request.form.get('resultType')
    searchDept = request.form.get('department')
    searchNum = request.form.get('number')
    searchName = request.form.get('name')
    searchCredit = request.form.get('credit')

    stringDept = "%{}%".format(searchDept)
    stringNum = "%{}%".format(searchNum)
    stringName = "%{}%".format(searchName)
    stringCredit = "%{}%".format(searchCredit)

    search_params = []
    if searchDept:
        search_params.append(custom_courses.department.like(stringDept))
    if searchNum:
        search_params.append(custom_courses.number.like(stringNum))
    if searchName:
        search_params.append(custom_courses.name.like(stringName))
    if searchCredit:
        search_params.append(custom_courses.credit.like(stringCredit))

    if resultType == "AND":
        # courses = custom_courses.query.filter(custom_courses.crn.like(stringCRN), custom_courses.name.like(stringName), custom_courses.types.like(stringType), custom_courses.department.like(stringDept), custom_courses.credit.like(stringCredit), custom_courses.days.like(stringDay), custom_courses.time.like(stringTime), custom_courses.professor.like(stringProf)).all()
        courses = db.session.execute('SELECT * FROM custom_courses WHERE \
                                    department LIKE :stringDept AND \
                                    number LIKE :stringNum AND \
                                    name LIKE :stringName AND \
                                    credit LIKE :stringCredit',
                                    {'stringDept':stringDept,'stringNum':stringNum,'stringName':stringName,'stringCredit':stringCredit})
    if resultType == "OR":
        if len(search_params) == 0:
            courses = db.session.execute('SELECT * FROM custom_courses')
        else:
            courses = db.session.query(custom_courses).filter(or_(*search_params)).all()
    
    db.session.commit()
    
    return render_template("results.html", courses=courses)


@app.route("/insertdata")
def insert_data():
        
        # Insert into custom_courses 
        # db.session.execute('INSERT INTO custom_courses(department, number, name, credit) VALUES(:dept, :course_id, :label, :credit)',{'dept':dept,'course_id':course_id,'label':label,'credit':credit})
        # db.session.commit()

    return "No Data to Insert :)"


@app.route("/schedules", methods=['POST', 'GET'])
def schedules():
    all_users_netid = []
    all_users_major = []
    all_users_track = []
    all_users_courses = []
    major_dict = {'compe': 'Computer Engineering', 'ee': 'Electrical Engineering'}
    if request.method == "POST":
        if "search_by_track" in request.form:
            track_name = request.form.get('track_name')
            if track_name == "":
                for user in collection6.find():
                    netid = user.get('_id')
                    courses = user.get('course_list')
                    get_major = db.session.execute('SELECT major FROM user WHERE netid=:netid',{'netid':netid})
                    for m in get_major:
                        major = major_dict[m[0]]

                    get_track = db.session.execute('SELECT track_name FROM user WHERE netid=:netid',{'netid':netid})
                    
                    for t in get_track:
                        track = t[0]

                    all_users_netid.append(netid)
                    all_users_major.append(major)
                    all_users_track.append(track)
                    all_users_courses.append(courses)

            all_users_len = len(all_users_netid)


            # Tracks Table:
            # track_name, department, major

            # User Table:
            # netid, major, track_name

            search_track = db.session.execute('SELECT u.netid, u.major, u.track_name FROM user u INNER JOIN tracks t ON u.track_name = t.track_name WHERE t.track_name=:track_name', {'track_name':track_name})
            for user in search_track:
                unetid = user[0]
                get_major = user[1]
                umajor = major_dict[get_major]
                utrack = user[2]

                user = collection6.find_one({"_id": unetid})
                courses_planned = user['course_list']

                all_users_netid.append(unetid)
                all_users_major.append(umajor)
                all_users_track.append(utrack)
                all_users_courses.append(courses_planned)

            all_users_len = len(all_users_netid)
        
        return render_template("user_courses.html", all_users_len=all_users_len, all_users_netid=all_users_netid, all_users_major=all_users_major, all_users_track=all_users_track, all_users_courses=all_users_courses)

    else:
        for user in collection6.find():
            netid = user.get('_id')
            courses = user.get('course_list')
            get_major = db.session.execute('SELECT major FROM user WHERE netid=:netid',{'netid':netid})
            for m in get_major:
                major = major_dict[m[0]]

            get_track = db.session.execute('SELECT track_name FROM user WHERE netid=:netid',{'netid':netid})
            
            for t in get_track:
                track = t[0]

            all_users_netid.append(netid)
            all_users_major.append(major)
            all_users_track.append(track)
            all_users_courses.append(courses)

        all_users_len = len(all_users_netid)

        return render_template("user_courses.html", all_users_len=all_users_len, all_users_netid=all_users_netid, all_users_major=all_users_major, all_users_track=all_users_track, all_users_courses=all_users_courses)


# @app.route("/test")
# def test_insert():
#     stu = test('CompE', 'Systems')
#     db.session.add(stu)
#     db.session.commit()
#     return render_template("index.html")
