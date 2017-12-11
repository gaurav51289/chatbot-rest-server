import time
import calendar
from flask_api import FlaskAPI
from flask import request, jsonify
from remote_api_calls import getCategories, getProbabilityOfCandidate
import psycopg2
import itertools
import re
import string

DB_NAME = 'ubuntudb'
DB_ENDPOINT = 'localhost'
DB_USERNAME = 'ubuntu'
DB_PASSWORD = 'root'
DB_PORT = 5432  # default port
CANDIDATE_THRESHOLD = 5

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from html.entities import name2codepoint
from bs4 import BeautifulSoup
import json

regex = re.compile('[%s]' % re.escape(string.punctuation))
wordnet = WordNetLemmatizer()

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                else:
                    return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is

    return re.sub("&#?\w+;", fixup, text)


def cleanText(text):
    text = text.lower()
    soup = BeautifulSoup(unescape(text), "html.parser")
    text = soup.get_text()  # nltk.clean_html(unescape(text))

    tokens = word_tokenize(text)
    new_tokens = []
    for t in tokens:
        nt = regex.sub(u'', t)
        if not nt == u'' and nt not in stopwords.words('english'):
            new_tokens.append(wordnet.lemmatize(nt))

    text = " ".join(new_tokens)
    return text.encode('ascii', errors='ignore').decode()


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
                print(t)
                qset = answers_ids[t[0]]
                for c in t[1:]:
                    qset.intersection_update(answers_ids[c])

                qidlist.update(qset)

            print(qidlist)
            if len(qidlist) > CANDIDATE_THRESHOLD:
                return list(qidlist)
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
                answers.append(ans[0])
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
                print("QUESTION: " + question)

                que_cats = getCategories(cleanText(question))
                candidate_qids = getCandidateQids(que_cats)
                if candidate_qids is None or len(candidate_qids)<1:

                    response = jsonify({
                       'question': question,
                       'timestamp': calendar.timegm(time.gmtime()),
                       'answer': "Please give more details. I cannot understand your query.",
                       'probablity': '0'
                    })
                    return response

                candidateAnswers = getCandidateAnswers(candidate_qids)
                anslist = []
                for ans in candidateAnswers:
                    ansc = cleanText(ans)
                    print("ANSWER cleaned: " + ansc)
                    print("ANSWER raw: " + ans)
                    prob = getProbabilityOfCandidate(question, ansc)
                    print("Probablity: " + json.dumps(prob))
                    anslist.append((float(prob['probability']), ans))

                anslist = sorted(anslist, reverse=True)

                response = jsonify({
                    'question': question,
                    'timestamp': calendar.timegm(time.gmtime()),
                    'answer': anslist[0][1],
                    'probablity': str(anslist[0][0])
                })
                return response

    return app

