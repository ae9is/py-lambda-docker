import json
import sys


def handler(event, context):
  '''
  /torch/version
  '''
  print(f'Lambda using python {sys.version}')
  print('Trying to load torch...')
  import torch
  version = torch.__version__
  cuda = {
    'version': torch.version.cuda,
    'available': torch.cuda.is_available(),
  }
  body = {
    '__version__': version,
    'cuda': cuda,
  }
  response = {'statusCode': 200, 'body': json.dumps(body)}
  return response
