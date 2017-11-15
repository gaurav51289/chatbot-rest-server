import time, calendar

from flask_api import FlaskAPI
from flask import request, jsonify


def create_app():
    app = FlaskAPI(__name__, instance_relative_config=True)

    @app.route('/ask/', methods=['POST'])
    def ask():
        if request.method == "POST":
            question = str(request.data.get('question'))
            if question:
                response = jsonify({
                    'question': question,
                    'timestamp': calendar.timegm(time.gmtime()),
                    'answer': "Here is your answer..."
                })
                response.status_code = 200
                return response

    return app