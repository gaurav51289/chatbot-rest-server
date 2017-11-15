## REST API server for chatbot

### Start

1. `python run.py`


## cURL
`curl -X POST \
  http://localhost:5000/ask/ \
  -H 'cache-control: no-cache' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -H 'postman-token: 8c154f59-588f-5028-7d6b-86a049154b6e' \
  -F 'question="What is ubuntu?"'`
