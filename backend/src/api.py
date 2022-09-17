
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES


'''
GET /drinks
    it is a public endpoint
    it contains only the drink.short() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        data = [drink.short() for drink in drinks]

        return jsonify({"success": True, "drinks": data})
    except:
        abort(404)


'''
GET /drinks-detail
    it requires the 'get:drinks-detail' permission
    it contains the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_detailed_drinks(jwt):
    try:
        drinks = Drink.query.all()
        data = [drink.long() for drink in drinks]

        return jsonify({"success": True, "drinks": data})
    except:
        abort(404)

'''
POST /drinks
    it creates a new row in the drinks table
    it requires the 'post:drinks' permission
    it contains the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()

    try:
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        new_drink = Drink(title=title, recipe=json.dumps(recipe))

        new_drink.insert()

        drink = Drink.query.get_or_404(new_drink.id)

        drinks = [drink.long()]

        return jsonify({'sucess': True, "drinks": drinks})

    except:
        abort(422)


'''
PATCH /drinks/<id>
    where <id> is the existing model id
    it responds with a 404 error if <id> is not found
    it updates the corresponding row for <id>
    it requires the 'patch:drinks' permission
    it contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    body = request.get_json()
    try:
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink.query.get_or_404(id)

        drink.title = title
        drink.recipe = json.dumps(recipe)

        drink.update()

        drinks = [drink.long()]

        return jsonify({'sucess': True, 'drinks': drinks})

    except:
        abort(404)


'''

DELETE /drinks/<id>
    where <id> is the existing model id
    it responds with a 404 error if <id> is not found
    it deletes the corresponding row for <id>
    it requires the 'delete:drinks' permission
returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        drink = Drink.query.get_or_404(id)
        drink.delete()

        return jsonify({'sucess': True, 'delete': id})
    except:
        abort(404)


# Error Handling


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.get('description', 'error'),
    }), error.status_code
