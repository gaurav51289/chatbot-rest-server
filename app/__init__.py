import time, calendar

from flask_api import FlaskAPI
from flask import request, jsonify

from categorizer import getCategories


def create_app():
    app = FlaskAPI(__name__, instance_relative_config=True)

    @app.route('/ask/', methods=['POST'])
    def ask():
        if request.method == "POST":
            question = str(request.data.get('question'))
            if question:

                que_cats = getCategories(question)
                print('',end='')
                print('================================================================================')
                print('PREDICTED CATEGORIES FOR THE QUESTION')
                print('================================================================================')
                print(que_cats)

                response = jsonify({
                    'question': question,
                    'timestamp': calendar.timegm(time.gmtime()),
                    'answer': "Here is your answer...",
                    'message' : 'Check server console for QUE categories'
                })
                response.status_code = 200
                return response

    return app