import json
import os.path
import random
import time

from flask import Flask, request, jsonify, send_file
from sqlalchemy.exc import IntegrityError

from database import db_utils
from services.cache import r_conn, get_cache_key
from services.map import get_visited_map
from services.utils import paginated_data
from logging_config import logger


app = Flask(__name__)
ALLOWED_FILE_EXTENSIONS = {'json', 'geojson'}

@app.route('/user', methods=['POST'])
def user():
    try:
        tg_chat_id = request.form.get('tg_chat_id')
        if tg_chat_id:
            db_utils.create_user(tg_chat_id)
            return 'User successfully created', 201
    except IntegrityError as e:
        return 'User already exists', 400
    except Exception as e:
        return 'Server error {e}', 500


@app.route('/visits', methods=['GET', 'POST'])
def visits():
    if request.method == 'GET':
        try:
            tg_chat_id = int(request.args['tg_chat_id'])
            unit_flag = request.args['unit_flag']
            rel_map_path = get_visited_map(tg_chat_id, unit_flag)

            if rel_map_path is None:
                return 'Visited list is empty', 204

            while not os.path.exists(rel_map_path):
                time.sleep(0.1)
            abs_map_path = os.path.join(os.path.dirname(__file__), 'services', rel_map_path)
            return send_file(rel_map_path, as_attachment=True)
        except KeyError:
            return 'Mandatory parameters were not provided', 400
        except Exception as e:
            return f'{e}', 500
    elif request.method == 'POST':
        try:
            tg_chat_id = request.form['tg_chat_id']
            location = request.form['location']
            db_utils.add_visit(tg_chat_id=tg_chat_id, location=location)
            return 'Visit successfully added', 201
        except KeyError:
            return 'Mandatory parameters were not provided', 400
        except Exception as e:
            return f'{e}', 500


@app.route('/places', methods=['GET'])
def places():
    try:
        prompt = request.args['prompt'].capitalize()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('size', 10))

        cached_data = r_conn.get(prompt)
        if cached_data:
            data = json.loads(cached_data)
        else:
            data = db_utils.get_places(prompt)
            if not data:
                return 'Place not found', 404
            json_data = json.dumps(data)
            r_conn.set(prompt, json_data, ex=600)

        output = paginated_data(data, page, page_size)
        return output

    except KeyError:
        return 'Search prompt was not provided', 400
    except Exception as e:
        return f'{e}', 500


@app.route('/unvisited', methods=['GET'])
def get_unvisited_districts():
    try:
        tg_chat_id = int(request.args['tg_chat_id'])
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('size', 10))
        rand = eval(request.args.get('random', default='False'))

        data = db_utils.get_unvisited_districts(tg_chat_id=tg_chat_id)
        if not data:
            return 'No data', 404
        if rand is True:
            random_district = random.choice(data)
            return random_district
        output = paginated_data(data, page, page_size)
        return output
    except KeyError:
        return 'tg_chat_id was not provided', 400
    except Exception as e:
        return f'{e}', 500


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_EXTENSIONS


@app.route('/geojson', methods=['GET', 'POST'])
def geojson():
    if request.method == 'GET':
        try:
            tg_chat_id = int(request.args['tg_chat_id'])
            data = db_utils.get_visits_json(tg_chat_id=tg_chat_id)
            if data:
                return jsonify({'data': data})
            return 'visits list is empty', 404
        except Exception as e:
            return f'{e}', 500
    elif request.method == 'POST':
        try:
            tg_chat_id = request.json['tg_chat_id']
            data = json.loads(request.json['data'])
            db_utils.import_json(tg_chat_id=tg_chat_id, data=data)
            return 'Visits successfully imported', 201
        except KeyError:
            return "Json doesn't contain necessary fields. Check the geojson specs", 400
        except Exception as e:
            return f'Unsupported data format - {e}', 415


if __name__=='__main__':
    app.run()
