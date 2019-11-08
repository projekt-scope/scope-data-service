import os
import time
import glob
from app import app
from flask import render_template

from app.api.scope_service_api_calls import get_named_graphs


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/TS", methods=["GET"])
@app.route("/ts", methods=["GET"])
@app.route("/Ts", methods=["GET"])
def homeTS():
    try:
        insert_attribute = os.environ["RENDER_INSERT_ATTRIBUTE"]
    except:
        insert_attribute="True"

    if insert_attribute=="True":
        insert_attribute=True
    else:
         insert_attribute=False

    examples = get_named_graphs()
    delet_old_json()

    return render_template("render_TS_based.html", examples=examples,insert_attribute=insert_attribute)


def delet_old_json():
    # files = []
    dirpath = os.getcwd()
    path = os.path.join(dirpath, "src/app/render/static/shapes")
    minutes = 1
    time_in_secs = time.time() - (minutes * 60)
    for file in glob.glob(path + "/*.json"):
        stat = os.stat(file)
        if stat.st_mtime <= time_in_secs:
            # print(f'delete {file}')
            os.remove(file)
