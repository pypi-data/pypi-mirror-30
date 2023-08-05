#!flask/bin/python
import datetime

from flask import Flask, jsonify, request, abort, make_response

from cbc_api.geo.msdn import MSDN
from cbc_api.schedule.schedule import Schedule

app = Flask(__name__)

VALID_SOLVERS = ['CBC', 'SCIP']

@app.route('/cbc_datakind/api/v1.0/test', methods=['GET'])
def test():
    """
    Used to test to make sure the API is running correctly
    """
    return jsonify({'message':'Hello, friend! :)'})

@app.route('/cbc_datakind/api/v1.0/schedule', methods=['POST'])
def schedule_activities():
    """
    Uses the cbc_schedule package to schedule caseworker
    activities
    """
    # Check to see if there is a JSON in the request
    if not request.json:
        error = {'error':'JSON not found'}
        return make_response(jsonify(error),400)

    # Convert strings in the JSON file to integers
    configs = json_string_to_int(request.json)

    # Parse the query parameters
    method = request.args.get('method')
    if method is None:
        method = 'pyschedule'

    # Find directions
    start = datetime.datetime.now()
    schedule = Schedule(configs)
    schedule.schedule_activities(method=method)
    end = datetime.datetime.now()
    run_time = str(end-start)

    return jsonify({
        'schedule' : schedule.configs,
        'run_time' : run_time
        })

@app.route('/cbc_datakind/api/v1.0/convert_address', methods=['GET'])
def convert_address():
    """
    Converts an address to lat/long coordinates
    """
    # Get the query parameters from the request
    street = request.args.get('street')
    if street is None:
        error = {'error' : 'Street not defined'}
        return make_response(jsonify(error),400)

    city = request.args.get('city')
    if city is None:
        error = {'error' : 'City not defined'}
        return make_response(jsonify(error),400)

    state = request.args.get('state')
    if state is None:
        error = {'error' : 'State not defined'}
        return make_response(jsonify(error),400)

    zip_code = request.args.get('zipCode')
    if zip_code is None:
        error = {'error' : 'Zip Code not defined'}
        return make_response(jsonify(error),400)

    # Convert the address to coordinates
    msdn = MSDN()
    coordinates = msdn.convert_address(
        street=street,
        city=city,
        state=state,
        zip_code=zip_code
    )
    
    return jsonify({
        'coordinates' : coordinates,
        'address' : {
            'street' : street,
            'city' : city,
            'state' : state,
            'zipCode' : zip_code
        }
    })

def json_string_to_int(config):
    """
    Converts strings from the json object to
    intergers so they can be used in the scheduler
    """
    config['origin']['coordinates'] = convert_coordinates(
            config['origin']['coordinates'])
    config['destination']['coordinates'] = convert_coordinates(
            config['destination']['coordinates'])

    activities = config['activities']
    for activity in activities:
        activity['coordinates'] = convert_coordinates(activity['coordinates'])

    return config

def convert_coordinates(coords):
    """
    Converts coordinates to flaots
    """
    coords = [float(x) for x in coords]
    return coords
