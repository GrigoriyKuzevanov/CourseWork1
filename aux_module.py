import os
import requests
import json


def get_id_by_screen_name(screen_name, token):
    url = 'https://api.vk.com/method/users.get'
    params = {'user_ids': screen_name, 'access_token': token, 'v': '5.131'}
    resp = requests.get(url, params=params)
    info = resp.json()
    id_by_screen_name = info['response'][0]['id']
    return id_by_screen_name


def max_size(items_list):
    size_max = 0
    result = dict()
    for item in items_list:
        current_size = item['height'] * item['width']
        if current_size >= size_max:
            result['size'] = item['type']
            result['url'] = item['url']
            size_max = current_size
    return result


def path_builder(file_name):
    path_base = os.getcwd()
    file_path = os.path.join(path_base, 'load_files', f"{file_name}.jpg")
    return file_path


def data_to_json(data):
    with open('out_data.json', 'w') as f:
        json.dump(data, f)
        print(f'json файл сформирован')
