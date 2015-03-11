from flask import Flask, request
from flask.ext.restful import Resource, Api

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
