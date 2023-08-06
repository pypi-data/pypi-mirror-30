import requests
import logging


class MissingIDParameter(Exception):
  def __init__(self,):
    Exception.__init__(self, 'The \'id\' parameter must be included in the request')


class DRFClient:
  def __init__(self, base_url, token):
    self.requests = ApiRequest(base_url, token)
    self.client = Stage(requester=self.requests)


class ApiRequest:
  def __init__(self, base_url, token):
    self.base_url = base_url
    self.headers = {'Authorization': str(token)}

  def get_request(self, request_url):
    # print(self.base_url + request_url)
    r = requests.get(self.base_url + str(request_url), headers=self.headers)
    response = {'status_code': r.status_code, 'response': r.json()}
    return response
    # if int(r.status_code / 100) == 2:
    # return r.json(), r.status_code
    # else:
    #   return r.text, r.status_code

  def post_request(self, request_url, data):
    r = requests.post(self.base_url + str(request_url), data=data, headers=self.headers)
    # print(r.text)
    response = {'status_code': r.status_code, 'response': r.json()}
    return response

  def put_request(self, request_url, data):
    r = requests.put(self.base_url + str(request_url), data=data, headers=self.headers)
    response = {'status_code': r.status_code, 'response': r.json()}
    return response

  def patch_request(self, request_url, data):
    r = requests.patch(self.base_url + str(request_url), data=data, headers=self.headers)
    response = {'status_code': r.status_code, 'response': r.json()}
    return response

  def delete_request(self, request_url):
    r = requests.delete(self.base_url + str(request_url), headers=self.headers)
    response = {'status_code': r.status_code, 'response': r.json()}
    return response


class Stage:
  def __init__(self, requester=None, path=[], name=None):
    self.name = name
    self.path = path
    self.requester = requester

  def __getattr__(self, item):
    self.path.append(item)
    return Stage(self.requester, self.path, item)

  def __call__(self, *args, **kwargs):

    request_url = '/{}/'.format(self.path[0])

    # Determine the request type (currently based on DRF format)
    # -------------------------------------------------------------------------

    if self.name.endswith('_list'):
      separator = '?'
      for key in kwargs:
        request_url += '{}{}={}'.format(separator, key, kwargs[key])
        if separator == '?':
          separator = '&'
      return self.requester.get_request(request_url)

    elif self.name.endswith('_read'):
      if 'id' not in kwargs:
        raise MissingIDParameter
      request_url += str(kwargs['id']) + '/'
      return self.requester.get_request(request_url)

    elif self.name.endswith('_create'):
      return self.requester.post_request(request_url, kwargs)

    elif self.name.endswith('_update'):
      if 'id' not in kwargs:
        raise MissingIDParameter
      request_url += str(kwargs['id']) + '/'
      return self.requester.put_request(request_url, kwargs)

    elif self.name.endswith('_partial_update'):
      if 'id' not in kwargs:
        raise MissingIDParameter
      request_url += str(kwargs['id']) + '/'
      return self.requester.patch_request(request_url, kwargs)

    elif self.name.endswith('_delete'):
      if 'id' not in kwargs:
        raise MissingIDParameter
      request_url += str(kwargs['id']) + '/'
      return self.requester.delete_request(request_url)

    else:
      raise Exception('Unknown request type')