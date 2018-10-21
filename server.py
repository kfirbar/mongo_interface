from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import Flask, request, current_app, send_from_directory
from flask_restful import Resource, Api
from pymongo import MongoClient
import json
import argparse


class Find(Resource):
    def get(self, collection):
        mongo_client = current_app.config['mongo_client']
        args = current_app.config['args']
        db = mongo_client[args.mongodb_db]
        query = request.form.get('query', default="", type=str)
        token = request.form.get('token', default="", type=str)
        if token != args.token:
            results = ["The token you provided doesn't match our records."]
        else:
            query = json.loads(query)
            results = db[collection].find(query).limit(2)
        return dumps(results)


class Aggregate(Resource):
    def get(self, collection):
        mongo_client = current_app.config['mongo_client']
        args = current_app.config['args']
        db = mongo_client[args.mongodb_db]
        query = request.form.get('query', default="", type=str)
        token = request.form.get('token', default="", type=str)
        if token != args.token:
            results = ["The token you provided doesn't match our records."]
        else:
            query = json.loads(query)
            results = db[collection].aggregate(query)
        return dumps(results)


def create_app(args, debug=False):
    app = Flask(__name__)
    app.debug = debug
    app.config["args"] = args
    client = MongoClient('mongodb://' + args.mongodb_user + ':' + args.mongodb_password + '@'
                         + args.mongodb_host + ':' + str(args.mongodb_port) + '/' + args.mongodb_db)
    app.config["mongo_client"] = client
    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", help="the language we train on (e.g., eng, jpn)", default="eng")
    parser.add_argument("--mongodb_host", help="the mongo db host", default="localhost")
    parser.add_argument("--mongodb_port", help="the mongo db port", type=int, default=27017)
    parser.add_argument("--mongodb_user", help="the mongo db username", default="")
    parser.add_argument("--mongodb_password", help="the mongo db password", default="")
    parser.add_argument("--mongodb_db", help="the mongo db database", default="")
    parser.add_argument("--server_port", help="the mongo db port", type=int, default=9000)
    parser.add_argument("--token", help="the server token", type=str, default="kjh92837dshjdhfn8nx")

    args = parser.parse_args()

    app = create_app(args, debug=False)
    api = Api(app)
    # Routing
    api.add_resource(Find, '/find/<string:collection>')
    api.add_resource(Aggregate, '/aggregate/<string:collection>')

    # [TODO] Disable debug when in production
    app.run(host='0.0.0.0', port=args.server_port, debug=True, ssl_context='adhoc')


if __name__ == "__main__":
    main()
