from flask import Flask
from flask import render_template
from flask import Response
from flask import jsonify
from flask import request
import numpy as np
import pandas as pd
import time

from src.csv2json import filter_data
from src.gsheet2csv import load_gspread
from src.crunch_numbers import text_data, pie_data, map_data, numbers_data

app = Flask(__name__)
time_cached_gspread = time.time()

def load_data(**params):
    global time_cached_gspread
    elapsed = time.time() - time_cached_gspread
    if elapsed > 60*60:
        print('Reloading cache from gspread (last time was {}s ago)'.format(np.round(elapsed, 3)))
        load_gspread()
        time_cached_gspread = time.time()

    return filter_data(**params)

@app.route('/data/json/')
def get_json():
    # Load params
    params = {
        'n_days': int(request.args.get('n_days', 0)),
        'action': request.args.get('action', None),
    }

    # Get data
    data = load_data(**params)

    return jsonify(data)



@app.route('/')
def hello_world(n_days=0):
    # Load params
    params = {
        'n_days': int(request.args.get('n_days', 0)),
        'region': request.args.get('region', None)
    }

    # Get data
    data = load_data(**params)

    # Crunch numbers
    feed_text = text_data(data)
    feed_pie = pie_data(data)
    feed_map = map_data(data)
    feed_numbers = numbers_data(data)

    df = pd.read_csv('src/indicateur_departement.csv', sep='\t')
    list_dep = list(df.iloc[:, 1])


    return render_template('index.html', list_dep=list_dep, **feed_text, **feed_pie, **feed_map, **feed_numbers)