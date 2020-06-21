from bs4 import BeautifulSoup
import urllib.parse

from kov_utils.request import request
from kov_utils.kjson import load

from .url_creator import UrlCreator

url_creator = UrlCreator()

def get_pin_details(search_term: str, number_of_pins_to_get: int):
    pins_info = []
    saved_pins = 0
    bookmark = "Y2JVSG81V2sxcmNHRlpWM1J5VFVad1YxWllhR3BXYkhCNFdWVmtSMVl4U2xkV2FrNVhUVmRvTTFsWGN6RlNNazVKVW14a1YxSlZjRkZYVm1RMFVtc3hWMVZZWkdGU1YxSnZWV3hTVjFKc1dYaFZhemxZWWxaYWVsVXlOVTlYUjBwSVZXMW9XbFpXVlhoV01GcExaRWRPUms1WGFHaE5WbGt5Vm1wS01HRXhWWGxTYTJScFUwVmFVMVpyVlRGaFJscHlWbFJHYTFKc1NsZFdWekExWVVaS1ZWSnNiRmROYWtVd1ZrUktWMk5zVG5WVGJGWllVMFZLU1ZkWGVGWmxSMDVYVkd4c2FGSlVWbk5aYkZWM1pVWlplRmRzVGxkaVZscDVWRlpTWVZaV1drWlRiRUpYVFVkb2RsWlZXbGRqTVdSMFpFWkNVbFpFUVRWYWExcFhVMWRLTmxWck9WZE5XRUpIVm0wd2VFMUdiRmRUYTJoc1UwVktXVmxzVWtkWlZsSldWMjVPVDJKR1dsWlZNbmgzVmpBeFIyTkliRmRTYkZwVVZqSnpkMlF3TVZkV2JGSllVakZLVUZadGRGZFpWMDVYVlZob1ZtRXpRbEJXYkZKelZteGtXV05HWkZaU2EzQkhWV3hTUjFkR1duTlRiRUphWVRGV05GWXdXbUZXVmxaelVXeE9VMDFzUlhkV2FrbzBZVEZSZVZKWVpFNVhSa3BVVm10V1lXRkdiSE5YYTJSUFZteEtNRmt3YUU5aFJrcDBaSHBLVmxac1NsUldSRVphWlVaT2RWTnNhR2hOVlhCTlYxZDRWbVZIVWtkVWJrWm9VbXhhYjFSV1duZFhiR1IwWkVWYVVGWnJTbE5WUmxGNFQwVTFkRlpZWkZCV1Jtc3dWREZrUmsxVk5UWmhSM2hoVmtWYWIxUldaR0ZoVlRGWVYyMXNUMkpWVlhwWGEyUktUVlV4V0ZSdGJFOWxiSEJ5VjIxd1NtVnJOVWhWVkZKUFVqRnNOVlJyVWtaa01EbFZWVmh3WVdGclduRlhiVEZPVFZVeFNGWllhRkJXUjAxNVZGVlNVbVZyTlZsbFJUbFRWbTFSTkdaSFZUTk5NbGt6V1dwcmVVMVVTWHBhYW1NelRtcE5OVTU2U21wTmJVVjRXVEpSTkU1cVZtaGFiVlY2V2tSS2ExbHFaelJhUkZWNFRUSk9hMWxVV21sTmVsbDNXbFJaTlU1RVNYaGFWRUY0VG5wbk5VMVhVamhVYTFaWVprRTlQUT09fFVIbzVjR0Z1Um1saE1GSk9Tek5PYWxwNk1XWk5ha2t4V0hrd2VHWkVWWGhPVkUxNFRVZEZORTFYVG1oYVJGRXlXbXBuTVU5RWEzZGFSMDVvVFZkUk0wMXFUbXROZWtwcFRtMVNhMDVFYkd0T2FtaHRXbTFLYkZwVVdYbGFWRVp0VFhwVmVVNUVhelJaZW1OM1drUk5lRTF0VWpoVWExWllaa0U5UFE9PXw4ZDE5ZTJjMTBlMzliMjNhYzhhNDg3OWJhMWIxYTQ3NDhhNmNhZDVmYWRhMDZhYzAxNjdhZDQ3MTZmN2E3NmIwfE5FV3w="

    while True:
        url = url_creator.pins_api_url(search_term, bookmarks=bookmark)
        response = request(url).json()
        print('requested:', url)
        
        if 'resource_response' in response:
            resource = response['resource_response']
            data = resource['data']
            bookmark = resource['bookmark']
        
            if 'results' in data:
                results = data['results']
            
                for elem in results:
                    details = {}
                    title = elem['title']
                    
                    # if title == None or title == "":
                    #     continue

                    pin_id = elem['id']
                    pin_description = elem['description']
                    images = elem['images']

                    if 'orig' in images and 'url' in images['orig']:
                        img_url = images['orig']['url']
                    else:
                        img_url = images[-1]['url']
                    
                    details['title'] = title
                    details['pin_id'] = pin_id
                    details['pin_description'] = pin_description
                    details['img_url'] = img_url

                    pins_info.append(details)
                    saved_pins += 1

                    if number_of_pins_to_get == saved_pins:
                        return pins_info
                
    return None

# first 25 elements - https://www.pinterest.com/resource/BaseSearchResource/get/?source_url=/search/pins/?q=carpart&data={"options":{"isPrefetch":false,"query":"carpart","scope":"pins"},"context":{}}&_=1591293832003