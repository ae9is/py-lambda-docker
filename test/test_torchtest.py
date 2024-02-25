import requests as req
import packaging.version as vers


def test_torchtest(port=5000):
  """
  Test /torchtest

  Args:
    port: Port that /torchtest endpoint is at
  """
  url = f'http://localhost:{port}/torchtest'
  response: req.Response = req.request('POST', url)
  assert response.status_code == 200
  output = response.json() or {}
  print(f'response: {output}')
  pytorch_version = output['__version__']
  current_version = vers.parse(pytorch_version)
  min_version = vers.parse('2.2.0')
  assert current_version >= min_version


if __name__ == '__main__':
  print('Testing /torchtest ...')
  test_torchtest()
  print('Done testing')
