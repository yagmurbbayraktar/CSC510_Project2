"""
The module app holds the function related to flask app and database.
"""
"""Copyright 2022 Tejas Prabhu

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""
from flask import Flask, render_template, request, redirect, url_for  # noqa: E402
from flask_paginate import Pagination, get_page_args  # noqa: E402
from flask_pymongo import PyMongo  # noqa: E402
import pandas as pd  # noqa: E402
from pandas import DataFrame  # noqa: E402
import re  # noqa: E402
import numpy as np  # noqa: E402
import os  # noqa: E402
try:
    from src.cv_parser import cvAnalizer  # noqa: E402
except:  # noqa: E722
    from cv_parser import cvAnalizer  # noqa: E402
from werkzeug.utils import secure_filename  # noqa: E402
app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/job_analyzer"
mongodb_client = PyMongo(app)
db = mongodb_client.db
app.config['UPLOAD_FOLDER'] = 'upload/'

string = ""


@app.route('/upload')
def upload_file():
    """
    Route: '/upload'
    The upload function renders the upload.html page.
    """
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    """
    Route: '/uploader'
    The uploader function requires users to take a local file (resume) as a input, it will save the
    file in the program root path And then, will scan the resume through to find the relative skills
    maybe used.
    """
    if request.method == 'POST':
        f = request.files['file']
        print(request.files)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        list1 = cvAnalizer(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        global string
        string = ""
        for each in list1:
            string += each
            string += ","

        return render_template('uploadsuccess.html', string=string)

    else:

        return render_template('upload.html')

#get_results does calculation for pagination by setting page offset. 
def get_results(table, offset=0, per_page=5):
    return table[offset: offset+per_page]


@app.route('/')
def index():
    """
    Route: '/'
    The index function renders the index.html page.
    """
    return render_template('index.html')


@app.route('/search/', methods=('GET', 'POST'))
def search():
    """
    Route: '/search/'
    The search function takes data input from form and redirects to 
    results route while sending all the data via POST method.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        type = request.form.get('type')
        skills = request.form.get('skills')
        location = request.form.get('location')
        companyName = request.form.get('companyName')
        return redirect(url_for('results', title=title, type=type, skills=skills, location=location,
                                companyName=companyName))
    return render_template('get_job_postings.html')


@app.route('/search2/', methods=('GET', 'POST'))
def search2():
    """
    Route: '/search2/'
    The search2 function renders the get_job_postings.html.
    After the CV is Parsed this send data to be displayed for suggestions. 
    """
    if request.method == 'POST':
        title = request.form.get('title')
        type = request.form.get('type')
        skills = request.form.get('skills')
        location = request.form.get('location')
        companyName = request.form.get('companyName')
        return redirect(url_for('results', title=title, type=type, skills=skills, location=location,
                                companyName=companyName))
    return render_template('get_job_postings2.html', string=string)


@app.route('/results/')
def results():
    """
    Route: '/results/'
    The search function renders the get_job_postings.html
    Takes data from the search route and render job postings based on that.
    """
    title = request.args['title']
    type = request.args['type']
    skills_set = request.args['skills']
    location = request.args['location']
    companyName_set = request.args['companyName']
    skills_list = [s.strip() for s in skills_set.split(',')]
    company_list = [c.strip() for c in companyName_set.split(',')]
    job_df = get_job_df(title=title, type=type, skills_list=skills_list,
                        location=location, company_list=company_list, db=db)
    job_count = job_df.shape[0]
    if job_df.empty:
        job_count = 0
        return render_template('no_jobs.html', job_count=job_count)
    job_df = job_df.drop('Job Description', axis=1)
    job_df = job_df.drop('_id', axis=1)
    job_df = job_df.drop('Industries', axis=1)
    job_df = job_df.drop('Job function', axis=1)
    job_df = job_df.drop('Total Applicants', axis=1)
    job_df['Job Link'] = '<a href=' + job_df['Job Link'] + '><div>' + " Apply " + '</div></a>'
    job_link = job_df.pop("Job Link")
    job_df.insert(7, "Job Link", job_link)
    job_df['Job Link'] = job_df['Job Link'].fillna('----')
    page, per_page, offset = list(get_page_args(page_parameter="page", per_page_parameter="per_page"))
    total = job_count
    Pagination_results = get_results(job_df, int(offset), int(per_page))
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    return render_template('job_posting.html', job_count=job_count,
                           tables=['''
 <style>
    .table-class {border-collapse: collapse;    margin: 24px 0;    font-size: 1em;
    font-family: sans-serif;    min-width: 500px;    box-shadow: 0 0 19px rgba(0, 0, 0, 0.16);}
    .table-class thead tr {background-color: #009878;    color: #ffffff;    text-align: left;}
    .table-class th,.table-class td {    text-align:center; padding: 12.4px 15.2px;}
    .table-class tbody tr {border-bottom: 1.1px solid #dddddd;}
    .table-class tbody tr:nth-of-type(even) {    background-color: #f3f3f3;}
    .table-class tbody tr:last-of-type {    border-bottom: 2.1px solid #009878;}
    .table-class tbody tr.active-row {  font-weight: bold;    color: #009878;}
    table tr th { text-align:center; }
 </style>
 ''' + Pagination_results.to_html(classes="table-class", render_links=True, escape=False)],
   titles=job_df.columns.values,  # noqa: E128
                           table=Pagination_results, page=page, per_page=per_page, pagination=pagination)  # noqa: E128


def add(db, job_data):
    """
    The add function adds the skills column and adds the job data to the database.
    """
    job_data['skills'] = [','.join(map(str, skill)) for skill in job_data['skills']]
    job_data['skills'] = job_data['skills'].replace(r'^\s*$', np.nan, regex=True)
    job_data['skills'] = job_data['skills'].fillna('----')
    db.jobs.insert_many(job_data.to_dict('records'))


def read_from_db(title, type, skills, location, companyName, db):
    """
    The read_from_db function reads the job details based on the input provided using regex.
    Returns a DataFrame with the details
    """
    job_title = title
    job_type = type
    skills = skills
    job_location = location
    company_name = companyName

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


def get_job_df(title, type, skills_list, location, company_list, db):
    """
    The get_job_df function searches all the job description from mango db database
    Based on multiple skills, company name and append all the results by removing the
    Duplicates rows and finally returns a DataFrame with the details
    """
    job_df = DataFrame()
    if skills_list and company_list:
        for skills in skills_list:
            for companyName in company_list:
                temp_df = read_from_db(title, type, skills, location, companyName, db)
                job_df = pd.concat([temp_df, job_df])
    elif skills_list:
        companyName = ""
        for skills in skills_list:
            temp_df = read_from_db(title, type, skills, location, companyName, db)
            job_df = pd.concat([temp_df, job_df])
    elif company_list:
        skills = ""
        for companyName in company_list:
            temp_df = read_from_db(title, type, skills, location, companyName, db)
            job_df = pd.concat([temp_df, job_df])
    dup_subsets = ['Job Title', 'Company Name', 'Location', 'Date Posted', 'Seniority level', 'Employment type',
                   'Job Description', 'Job function', 'Total Applicants']
    job_df = job_df.drop_duplicates(subset=dup_subsets).reset_index().drop('index', axis=1)
    job_df.index = np.arange(1, len(job_df)+1)
    return job_df
