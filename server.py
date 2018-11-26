import hashlib
import json

from flask import Flask
from flask import request
from flask_cors import CORS
from database import CogCompLoggerDB


class CogCompLogger:

    def __init__(self, secret):
        self.secret = "DEFAULT"
        self.secret_md5 = ""
        self.app = Flask(__name__)
        CORS(self.app)
        self.set_secret(secret)
        self.db = CogCompLoggerDB()

    def set_secret(self, secret):
        if secret == self.secret:
            print("Security Error: your secret is public knowledge.")
            print("Exiting...")
            self.end()
        elif secret == self.secret + "_ENFORCE":
            print("Security Warning, but enforced to continue")
        self.secret = secret
        self.secret_md5 = hashlib.sha224(self.secret.encode('utf-8')).hexdigest()

    def check_login(self, args):
        if 'cookie' not in args:
            return False
        if args['cookie'] == self.secret_md5:
            return True
        return False

    def handle_root(self):
        return "No action is taken."

    def handle_manage(self):
        args_dict = request.args
        invalid_form = {
            'status': 'FAILURE',
            'action': 'INVALID'
        }
        if 'action' not in args_dict:
            return json.dumps(invalid_form)

        if args_dict['action'] == 'login':
            ret_form = {
                'status': 'FAILURE',
                'action': 'login',
                'cookie': 'none'
            }
            if 'secret' not in args_dict:
                return json.dumps(ret_form)
            if args_dict['secret'] == self.secret:
                ret_form['status'] = 'SUCCESS'
                ret_form['cookie'] = self.secret_md5
            return json.dumps(ret_form)

        if args_dict['action'] == 'register':
            ret_form = {
                'status': 'FAILURE',
                'action': 'register'
            }
            if 'entry_name' not in args_dict or 'entry_key' not in args_dict:
                return json.dumps(ret_form)
            # TODO WHERE LEFT OFF
            self.db.create_new_entry(args_dict['entry_name'], args_dict['entry_key'])

        return json.dumps(invalid_form)

    def start(self, localhost=False, port=80):
        self.app.add_url_rule("/", "", self.handle_root, methods=['POST', 'GET'])
        self.app.add_url_rule("/manage", "manage", self.handle_manage, methods=['POST', 'GET'])
        if localhost:
            self.app.run(ssl_context='adhoc', port=port)
        else:
            self.app.run(host='0.0.0.0', port=port, ssl_context='adhoc')

    def end(self):
        exit(0)


if __name__ == "__main__":
    logger = CogCompLogger("DEFAULT_ENFORCE")
    logger.start(localhost=True, port=5000)