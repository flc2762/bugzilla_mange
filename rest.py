import requests
import json

import sys     
reload(sys)     
sys.setdefaultencoding('utf-8') 
class API(object):
    def __init__(self, base_url, insecure = False, token = None, api_key = None):
        self.base_url = base_url
        self.insecure = insecure
        self.headers = {"User-Agent": 'pybz-rest'}
        self.token = token
        self.api_key = api_key

        if self.base_url is None or self.base_url == "":
            self.handle_error('base_url not optional')

        if not self.base_url.endswith("/"):
            self.base_url = self.base_url + "/"

        if not self.base_url.endswith("rest/"):
            self.base_url = self.base_url + "rest/"

        if self.insecure:
            if hasattr(requests, "packages"):
                requests.packages.urllib3.disable_warnings()

        self.session = requests.Session()

        if self.api_key:
            self.session.params['api_key'] = self.api_key

    def handle_error(self, message):
        raise Exception(message)

    def request(self, method, path, **kwargs):
        url = self.base_url + path
        headers = self.headers.copy()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        kwargs['verify'] = not self.insecure
        try:
            return self.session.request(method, url, **kwargs).json()
        except requests.exceptions.SSLError:
            return {'message': 'Invalid SSL certificates, enable insecure access.'}
        except:
            return {'message': "Invalid rest endpoint '%s'"%url}

    def login(self, username, password):
        if username is None or password is None or password == "":
            self.handle_error('Cannot login without username and password')
        else:
            result = self.request('GET', 'login', params = {
                'login': username,
                'password': password})
            if 'token' in result:
                self.token = result['token']
                self.session.params['token'] = self.token
            else:
                self.handle_error(result['message'])

    def logout(self):
        if self.token:
            result = self.request('GET', 'logout')
            if 'message' in result:
                self.handle_error(result['message'])

    def bug_get(self, params):
        result = self.request('GET', 'bug', params = params)
        if 'bugs' in result:
            return result['bugs']
        else:
            if 'message' in result:
                self.handle_error(result['message'])
    
    def bug_get_id_all_info(self, params):
        str_bugid = str(params['id'])
        path = 'bug/' + str_bugid
        result = self.request('GET', path)
        return result

    def bug_get_all_info(self, params):
        str_bugid = str(params['id'])
        path = 'bug/' + str_bugid + '/comment'
        result = self.request('GET', path)
        return result

    def bug_set(self, params):
        bid = params['ids'][0]
        result = self.request('PUT', 'bug/' + str(bid),
                data = json.dumps(params), headers={"content-type": "application/json"})
        if 'bugs' in result:
            return result['bugs']
        else:
            self.handle_error(result['message'])

    def bug_new(self, params):
        result = self.request('POST', 'bug',
                data = json.dumps(params), headers={"content-type": "application/json"})
        if 'bugs' in result:
            return result['bugs']
        else:
            self.handle_error(result['message'])

    def list_fields(self):
        result = self.request('GET', 'field/bug')
        if 'fields' in result:
            return [f['name'] for f in result['fields'] if 'name' in f
                    and f['name'] != 'bug_id']
        else:
            self.handle_error("can't retrieve fields: '%s'" % result['message'])

    def list_products(self):
        result = self.request('GET', 'product', {'type': 'accessible'})
        if 'products' in result:
            return [p['name'] for p in result['products'] if 'name' in p]
        else:
            self.handle_error("can't retrieve products: '%s'" % result['message'])

    def list_components(self, product):
        result = self.request('GET', 'product', {'names': product})
        if 'products' in result:
            for p in result['products']:
                if 'name' in p and p['name'].lower() == product.lower():
                    return [c['name'] for c in p['components']]
        else:
            self.handle_error("can't retrieve components: '%s'" % result['message'])

def main():
    print "hahahahahh.....\n"
	
if __name__ == '__main__':
    main()
