# Local api host for lambda using function url.
# You can also directly just execute for ex:
#  curl -XPOST http://localhost:3001/2015-03-31/functions/{lambda_function_name}/invocations -d '{"payload":"value"}'
# ref: https://github.com/aws/aws-sam-cli/issues/4299

import os
import requests

from flask import Flask, request, Response

LAMBDA_HOST = os.getenv('LAMBDA_HOST', '127.0.0.1:3001')
TARGET_URL = 'http://{}/2015-03-31/functions/{}/invocations'

app = Flask(__name__)


@app.route('/<function>', methods=['GET', 'POST'])
def forward_request(function):
  url = TARGET_URL.format(LAMBDA_HOST, function)
  # All request headers are stored in request.headers.environ,
  #  but this dictionary also contains WSGI specific headers
  #  that are not valid to post and will error.
  # For now, just pass on specific headers.
  headers = {'Content-Type': f'{request.content_type}', 'Content-Length': f'{request.content_length}'}
  payload = {
    'httpMethod': request.method,
    'queryStringParameters': request.args.to_dict(),
    'body': request.get_data(as_text=True),
    'headers': headers,
  }
  lambda_resp = requests.post(url, json=payload, headers=headers)
  lambda_resp.raise_for_status()
  resp_data = lambda_resp.json()
  body = resp_data.get('body', {})
  status = resp_data.get('statusCode', 500)
  print(f'Received lambda response data: {resp_data}')
  cors = {'Access-Control-Allow-Origin': '*'}
  headers = resp_data.get('headers', {}) | cors
  resp = Response(body, status=status, headers=headers)
  return resp
