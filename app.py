from chalice.app import Chalice
from chalice.app import Rate

from chalicelib.bayesian_football import *
import json
import boto3  
import ast
import numpy as np

#from chalicelib.bayesian_football import NumpyEncoder, generate_trace

app = Chalice(app_name='bayesianfootball')

"""
@app.schedule(Rate(7, unit=Rate.DAYS))
@app.route('/trace')
def save_trace_to_s3():
    trace = generate_trace()
    json_data = json.dumps(trace, cls=NumpyEncoder)
    s3 = boto3.resource('s3')
    
    s3object = s3.Object('bayesian-soccer-traces-matthew-burke', 'latest_trace.json')
    
    s3object.put(
        Body=(bytes(json.dumps(json_data).encode('UTF-8')))
    )
    return {"response":"trace_updated"}
"""

@app.route('/')
def index():
    if False:     # make this to never evaluate as True
        dummy()
    return {'hello': 'world'}

def dummy():
    """
    Collection of all s3.client() functions.
    The sole purpose is to force Chalice to generate the right permissions in the policy.
    Does nothing and returns nothing.
    """
    s3 = boto3.client('s3')
    s3.put_object()
    s3.download_file()
    s3.get_object()
    s3.list_objects_v2()
    s3.get_bucket_location()


@app.route('/match/{home}/{away}', cors=True)
def match_prediction(home,away):
    teams = {'ARS': 0,
             'AVL': 1,
             'BOU': 2,
             'BRE': 3,
             'BHA': 4,
             'BUR': 5,
             'CHE': 6,
             'CRY': 7,
             'EVE': 8,
             'FUL': 9,
             'LIV': 10,
             'LUT': 11,
             'MCI': 12,
             'MUN': 13,
             'NEW': 14,
             'NFO': 15,
             'SHU': 16,
             'TOT': 17,
             'WHU': 18,
             'WOL': 19}

    seed = 0
    home_index = teams[home]
    away_index = teams[away]

    s3 = boto3.resource('s3')
    content_object = s3.Object('bayesian-soccer-traces-matthew-burke', 'latest_trace.json')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    trace = ast.literal_eval(json.loads(file_content))

    home_attack, away_attack = trace["atts"][seed][home_index], trace["atts"][seed][away_index]
    home_defence, away_defence = trace["defs"][seed][home_index], trace["defs"][seed][away_index]
    home_advantage = trace['home_advantage'][seed]
    intercept = trace["intercept"][seed]
    home_wins =0
    away_wins=0
    draws=0
    for i in range(100):
        home_goals, away_goals =predict_score(intercept,home_advantage,home_attack,away_defence, away_attack, home_defence)
        if home_goals > away_goals:
            home_wins+=1
        elif home_goals < away_goals:
            away_wins+=1
        else:
            draws+=1

    return {"response":{"home":home,
                        "away":away,
                        "predictions":{"home_wins": home_wins,
                                       "draws":draws,
                                       "away_wins":away_wins}}}
            

def predict_score(intercept,home_advantage,home_attack,away_defence, away_attack, home_defence):
    home_goals = np.random.poisson(np.exp(intercept + home_advantage  + home_attack + away_defence))
    away_goals = np.random.poisson(np.exp(intercept + away_attack + home_defence))
    return home_goals,away_goals


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
