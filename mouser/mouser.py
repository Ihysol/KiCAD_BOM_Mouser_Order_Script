import os, json, requests, uuid
import pandas as pd

import mouser.config as mouser_config
import bom_handler.config as bom_config

''' mouser API request skeleton '''
class MouserAPIRequest:

    url = None
    api_url = None
    method = None
    body = {}
    response = None
    api_key = None

    name = ''
    allowed_methods = ['GET', 'POST']
    operation = None
    operations = {}

    def __init__(self, operation, body={}):
        self.operation = operation
        (method, url) = self.operations.get(self.operation, ('', ''))

        self.api_url = mouser_config.BASE_URL + url
        self.method = method
        self.body = body

        try:
            self.api_key = os.environ[mouser_config.ENVIRONMENT_VARIABLE_API_KEY_NAME]
            self.url = f"{self.api_url}?apiKey={self.api_key}"
        except KeyError:
            raise ValueError("\"MOUSER_API_KEY\" environment variable not found! \n\n**Make sure to add your MOUSER_API_KEY to your environment variables!**")

        if operation not in self.operations:
            print(f'[{self.name}]\tInvalid Operation')
            print('-' * 10)
            return None

    def get(self, url):
        response = requests.get(url=url)
        return response

    def post(self, url, body):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(url=url, data=body, headers=headers)
        return response.text

    def run(self):
        print(f'{self.method}, {self.body}')
        if self.method == 'GET':
            self.response = self.get(self.url)
        elif self.method == 'POST':
            self.response = self.post(self.url, self.body)

        self.print_response() # print response
        return len(json.loads(self.response)["Errors"]) == 0 # if errors in response are empty, everything is fine

    def get_response(self):
        if self.response is not None:
            try:
                return json.loads(self.response)
            except json.decoder.JSONDecodeError:
                return self.response
        return {}

    def print_response(self):
        print(json.dumps(self.get_response(), indent=4, sort_keys=True))

''' api request class implementations '''
class MouserCartRequest(MouserAPIRequest):
    name = 'Cart'
    operations = {
        'get': ('GET', '/cart'),
        'update': ('POST', '/cart'),
        'insertitem': ('POST', '/cart/items/insert'),
        'updateitem': ('POST', '/cart/items/update'),
        'removeitem': ('POST', '/cart/item/remove'),
    }   
class MouserOrderRequest(MouserAPIRequest):
    name = 'Order'
    operations = {
        'get': ('GET', '/order'),
        'create': ('POST', '/order'),
        'getcurrencies': ('GET', '/order/currencies'),
        'getcountries': ('GET', '/order/countries'),
        'getquery': ('POST', 'order/options/query')
    }  #
    
    
class MouserOrderClient:
    # specify the field name you used to store all manifacturer names, at the moment ONLY mouser part numbers are working
    search_strings = [bom_config.CSV_MOUSER_COLUMN_NAME]
    # specify unwanted strings like "DNF" to be removed from the parts list
    # @note "DNF" ect. should NOT be specified as part number, please consider removing it, rather than specifying it here.
    # this is just a precaution to be able to generate a BOM, without modifying the KiCAD project itself.
    banned_strings = ["DNF", "None"]    

    def __init__(self):
        pass

    def process_request(self, request_type, operation, body={}):
        if request_type == "cart":
            return MouserCartRequest(operation, body).run()

    def json_from_data_array(self, data_array):
        self.parts_json = [] # json body buffer

        headers = [] # get headers form data array
        for header in data_array:
            headers.append(header)

        df = pd.DataFrame(data_array)    
        for idx, row in df.iterrows():
            self.parts_json.append({'MouserPartNumber': row[headers[0]], 'Quantity': int(row[headers[1]]), 'CustomerPartNumber':row[headers[2]]})
            
        return self.parts_json

    def order_parts_from_json(self, json):
        cart_uuid = uuid.uuid4()
        body = f"{{'CartKey': {cart_uuid}, 'CartItems': {json}}}"  
        return self.process_request('cart', 'insertitem', body=body)
