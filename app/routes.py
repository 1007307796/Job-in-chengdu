from app import app
from flask import render_template
from app.models import Jobs
import json
from sqlalchemy import distinct
 
@app.route('/')
def index():
    cities = {'cd':'成都市'}
    result  = Jobs.query.distinct().all()
    infos = []
    for item in result:
        info = []
        info.append(item.work_addr)
        info.append(item.job_name)
        info.append(item.detail_url)
        info.append(item.data_from)
        info.append(item.company_name)
        infos.append(info)
    return render_template('index.html',cities=cities,infos=infos)