import json


def handler(event, context):
  '''
  /healthz
  '''
  body = {
    'message': 'OK',
    'input': event,
  }
  response = {'statusCode': 200, 'body': json.dumps(body)}
  return response
