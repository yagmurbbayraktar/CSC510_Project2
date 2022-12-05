"""
The module app holds the function related to flask app and database.
"""
"""Copyright 2022 Tejas Prabhu

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""
from flask import Flask, render_template, request, redirect, url_for  # noqa: E402
from flask_paginate import Pagination, get_page_args
from flask_pymongo import PyMongo  # noqa: E402
from pandas import DataFrame  # noqa: E402
import re  # noqa: E402
import numpy as np  # noqa: E402
app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/job_analyzer"
mongodb_client = PyMongo(app)
db = mongodb_client.db

def get_results(table, offset=0, per_page=5):
    return table[offset: offset+per_page]

@app.route('/')
def index():
    """
    Route: '/'
    The index function renders the index.html page.
    """
    return render_template('index.html')


@app.route('/search', methods=('GET', 'POST'))
def search():
    """
    Route: '/search'
    The search function renders the get_job_postings.html.
    Upon submission fetches the job postings from the database and renders job_posting.html
    """
    if request.method == 'POST':
        # print("WE ARE HERE !!!!!!!!1")
        # print (request.form.get("skills"))
        # data = {'title':request.form.get('title'),'type':request.form.get('type'),'skills':request.form.get('skills'),'location':request.form.get('location'),'companyName':request.form.get('companyName')}
        # data = [request.form.get('title'),request.form.get('type'),request.form.get('skills'),request.form.get('location'),request.form.get('companyName')]
        title = request.form.get('title')
        type = request.form.get('type')
        skills = request.form.get('skills')
        location = request.form.get('location')
        companyName = request.form.get('companyName')
        return redirect(url_for('results',title=title, type=type, skills=skills, location=location, companyName=companyName))
    return render_template('get_job_postings.html')


def add(db, job_data):
    """
    The add function adds the skills column and adds the job data to the database.
    """
    job_data['skills'] = [','.join(map(str, skill)) for skill in job_data['skills']]
    job_data['skills'] = job_data['skills'].replace(r'^\s*$', np.nan, regex=True)
    job_data['skills'] = job_data['skills'].fillna('----')
    db.jobs.insert_many(job_data.to_dict('records'))


def read_from_db(request, db):
    """
    The read_from_db function reads the job details based on the input provided using regex.
    Returns a DataFrame with the details
    """
    job_title = request.form['title']
    job_type = request.form['type']
    job_location = request.form['location']
    company_name = request.form['companyName']
    skills = request.form['skills']

    regex_char = ['.', '+', '*', '?', '^', '$', '(', ')', '[', ']', '{', '}', '|']

    for char in regex_char:
        skills = skills.replace(char, '\\'+char)

    rgx_title = re.compile('.*' + job_title + '.*', re.IGNORECASE)
    rgx_type = re.compile('.*' + job_type + '.*', re.IGNORECASE)
    rgx_location = re.compile('.*' + job_location + '.*', re.IGNORECASE)
    rgx_company_name = re.compile('.*' + company_name + '.*', re.IGNORECASE)
    rgx_skills = re.compile('.*' + skills + '.*', re.IGNORECASE)

    data_filter = {}
    if job_title != '':
        data_filter['Job Title'] = rgx_title
    if job_type != '':
        data_filter['Employment type'] = rgx_type
    if job_location != '':
        data_filter['Location'] = rgx_location
    if company_name != '':
        data_filter['Company Name'] = rgx_company_name
    if skills != '':
        data_filter['skills'] = rgx_skills

    data = db.jobs.find(data_filter)
    return DataFrame(list(data))
