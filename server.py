import hashlib
import json

from flask import Flask
from flask import request
from flask import send_from_directory
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

    @staticmethod
    def handle_root(path):
        if path == "" or path is None:
            path = "index.html"
        return send_from_directory('./frontend', path)

    @staticmethod
    def handle_index():
        return send_from_directory('./frontend', 'index.html')

    def handle_manage(self):
        args_dict = request.values.to_dict()
        if request.get_json() is not None:
            args_dict.update(request.get_json())
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

        if args_dict['action'] == 'get_all_records':
            ret_form = {
                'status': 'FAILURE',
                'action': 'get_all_records'
            }
            if not self.check_login(args_dict):
                return json.dumps(ret_form)
            records = self.db.get_all_entries()
            ret_form['status'] = 'SUCCESS'
            ret_form['data'] = records
            return json.dumps(ret_form)

        if args_dict['action'] == 'register_record':
            ret_form = {
                'status': 'FAILURE',
                'action': 'register_record'
            }
            # Enforce login state
            if not self.check_login(args_dict):
                return json.dumps(ret_form)
            if 'entry_name' not in args_dict or 'entry_url' not in args_dict or 'entry_email' not in args_dict:
                return json.dumps(ret_form)
            if args_dict['entry_url'] == "REMOVE" and args_dict['entry_email'] == "REMOVE":
                status = self.db.remove_entry(args_dict['entry_name'])
            else:
                status = self.db.create_new_entry(args_dict['entry_name'], args_dict['entry_url'], args_dict['entry_email'])
            if status:
                ret_form['status'] = 'SUCCESS'
            return json.dumps(ret_form)

        return json.dumps(invalid_form)

    # TODO: Other queries? content?
    def handle_query(self):
        args_dict = request.args
        ret_form = {
            'action': 'INVALID',
            'result': 'none'
        }
        if 'action' not in args_dict:
            return json.dumps(ret_form)

        if args_dict['action'] == 'count':
            ret_form['action'] = 'count'
            ret_form['result'] = 0
            if 'entry_name' not in args_dict:
                return json.dumps(ret_form)
            ret_form['result'] = self.db.get_entry_count(args_dict['entry_name'])
            return json.dumps(ret_form)

        return json.dumps(ret_form)

    '''
    Handle actual logging, invoked by demos
    '''
    def handle_log(self):
        args_dict = request.args
        ret_form = {
            'action': 'INVALID',
            'result': 'none'
        }
        if 'entry_name' not in args_dict:
            return json.dumps(ret_form)
        if 'entry_key' not in args_dict:
            return json.dumps(ret_form)
        content = ""
        if 'content' in args_dict:
            content = args_dict['content']
        self.db.add_new_log(
            args_dict['entry_name'],
            args_dict['entry_key'],
            content
        )
        ret_form['result'] = 'SUCCESS'
        return json.dumps(ret_form)

    def start(self, localhost=False, port=80):
        self.app.add_url_rule("/", "", self.handle_index)
        self.app.add_url_rule("/<path:path>", "<path:path>", self.handle_root)
        self.app.add_url_rule("/manage", "manage", self.handle_manage, methods=['POST', 'GET'])
        self.app.add_url_rule("/query", "query", self.handle_query, methods=['POST', 'GET'])
        self.app.add_url_rule("/log", "log", self.handle_log, methods=['POST', 'GET'])
        if localhost:
            self.app.run(ssl_context='adhoc', port=port)
        else:
            self.app.run(host='0.0.0.0', port=port, ssl_context='adhoc')

    # TODO: Grace exist (release db etc.)
    def end(self):
        exit(0)


if __name__ == "__main__":
    logger = CogCompLogger("DEFAULT_ENFORCE")
    logger.start(localhost=True, port=5000)
