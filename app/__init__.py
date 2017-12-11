import time
import calendar
from flask_api import FlaskAPI
from flask import request, jsonify
from remote_api_calls import getCategories, getProbabilityOfCandidate
import psycopg2
import itertools

DB_NAME = 'ubuntudb'
DB_ENDPOINT = 'localhost'
DB_USERNAME = 'ubuntu'
DB_PASSWORD = 'root'
DB_PORT = 5432  # default port
CANDIDATE_THRESHOLD = 5


def getCandidateQids(categories):
    try:
        conn = psycopg2.connect(host=DB_ENDPOINT, port=DB_PORT,
                                user=DB_USERNAME, password=DB_PASSWORD, dbname=DB_NAME)
        cur = conn.cursor()
        answers_ids = {}

        for cat in categories:
            answers_ids[cat] = set()

        sql = "select qid from postscleaned_raw where qtags like '%<{}>%'"
        for cat in categories:
            nsql = sql.format(cat)
            cur.execute(nsql)
            qids = cur.fetchall()
            for idx in qids:
                answers_ids[cat].add(idx[0])

        qidlist = set()

        for ncats in range(len(categories), 1, -1):
            combs = itertools.combinations(categories, ncats)

            for t in combs:
                qset = answers_ids[t[0]]
                for c in t[1:]:
                    qset.intersection_update(answers_ids[c])

                qidlist.update(qset)

            if len(qidlist) > CANDIDATE_THRESHOLD:
                return list(qidlist)
    except Exception as err:
        print(err)
        raise err


def getCandidateAnswers(qidlist):
    try:
        conn = psycopg2.connect(host=DB_ENDPOINT, port=DB_PORT,
                                user=DB_USERNAME, password=DB_PASSWORD, dbname=DB_NAME)
        cur = conn.cursor()
        answers = []

        sql = "select abody from postscleaned_raw where qid = {} limit 1;"
        for qid in qidlist:
            nsql = sql.format(qid)
            cur.execute(nsql)
            ans = cur.fetchone()
            if ans is not None:
                answers.append(ans)
        return answers
    except Exception as err:
        print (err)
        raise err


def create_app():
    app = FlaskAPI(__name__, instance_relative_config=True)

    @app.route('/ask/', methods=['POST'])
    def ask():
        if request.method == "POST":
            question = str(request.data.get('question'))
            if question:

                que_cats = getCategories(question)
                candidate_qids = getCandidateQids(que_cats)
                candidateAnswers = getCandidateAnswers(candidate_qids)
                
                for ans in candidateAnswers:
                    prob1 = getProbabilityOfCandidate(question, ans)
                    print(prob1)

                response = jsonify({
                    'question': question,
                    'timestamp': calendar.timegm(time.gmtime()),
                    'answer': "Here is your answer...",
                    'message': 'Check server console for QUE categories'
                })
                response.status_code = 200
                return response

    return app
