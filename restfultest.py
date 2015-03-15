from flask import Flask, request, session, g, redirect, url_for
from flask import abort, render_template, flash, send_from_directory, Response
from flask.ext.restful import Resource, Api
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime as dtime

app = Flask(__name__)
api = Api(app)

todos = {}

@app.route("/")
def index():
    return str(todos)

class test(Resource):
    def get(self, todo_id):
        return {todo_id: todos[todo_id]}

    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}

    def delete(self, todo_id):
        del todos[todo_id]
        return "delete %s"%todo_id

api.add_resource(test, '/<string:todo_id>')


if __name__ == '__main__':
    app.run(debug=True)
