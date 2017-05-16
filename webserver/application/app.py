from flask import request, render_template, jsonify, url_for, redirect
from flask_cors import CORS
from .schema import schema
from ..index import app, db
from sqlalchemy.exc import IntegrityError
from .utils.auth import generate_token, requires_auth, verify_token
from flask_graphql import GraphQLView


# Add CORS for GraphQL
cors = CORS(app, resources={r"/graphql/*": {"origins": "*"}})

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/<path:path>', methods=['GET'])
def any_root_path(path):
    return render_template('index.html')
