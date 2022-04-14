import requests
import os
from progress.bar import IncrementalBar
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


class VkPhotoSaver:
    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_info_json(self, count):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': self.token,
            'v': '5.131',
            'rev': 1,
            'owner_id': self.user_id,
            'album_id': 'profile',
            'count': count,
            'extended': 1
        }
        resp = requests.get(url, params=params)
        info = resp.json()
        print(f'Фотографии из ВК получены')
        return info

    def get_photo_info(self, count=5):
        info = self.get_info_json(count)
        result = []
        for item in info['response']['items']:
            res = (max_size(item['sizes']))
            res['likes'] = item['likes']['count']
            res['upload_date'] = item['date']
            result.append(res)
        return result

    def load_files(self, count):
        if not os.path.isdir('load_files'):
            os.mkdir('load_files')
        files_list = self.get_photo_info(count)
        bar = IncrementalBar(' Загрузка файлов из ВК', max=len(files_list))
        name = -1
        for file in files_list:
            url = file['url']
            resp = requests.get(url)
            if resp.status_code == 200:
                if file['likes'] != name:
                    with open(path_builder(file['likes']), 'wb') as f:
                        f.write(resp.content)
                    name = file['likes']
                else:
                    with open(path_builder(file['upload_date']), 'wb') as f:
                        f.write(resp.content)
                bar.next()
            else:
                print(f'Ошибка загрузки, статус ответа: {resp.status_code}')
        bar.finish()
        print(f'Загрузка на компьютер завершена')


class YaDiskUpLoader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def upload_photo_to_disk(self, list_files):
        dir_path = f'photos from VK'
        create_dir_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': dir_path}
        response_dir = requests.put(create_dir_url, headers=headers, params=params)
        if response_dir.status_code == 201:
            print('Папка на Диске создана')
        elif response_dir.status_code == 409:
            print('Папка на Диске уже существует')
        else:
            print(f'Ошибка, статус ответа: {response_dir.status_code}')
        data = []
        bar = IncrementalBar(' Загрузка файлов на Яндекс.диск', max=len(list_files))
        name = -1
        for file in list_files:
            file_info = dict()
            url = file['url']
            if file['likes'] != name:
                path = f"{dir_path}/{file['likes']}.jpg"
                file_info['file_name'] = f"{file['likes']}.jpg"
            else:
                path = f"{dir_path}/{file['upload_date']}.jpg"
                file_info['file_name'] = f"{file['upload_date']}.jpg"
            file_info['size'] = file['size']
            data.append(file_info)
            name = file['likes']
            upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = self.get_headers()
            params = {'url': url, 'path': path}
            response = requests.post(upload_url, headers=headers, params=params)
            if response.status_code != 202:
                print(f'Ошибка загрузки, код ответа: {response.status_code}')
            else:
                bar.next()
        bar.finish()
        print(f'Загрузка на Яндекс Диск завершена')
        data_to_json(data)


def main():
    token_vk = input('Введите токен доступа ВК: ')
    while True:
        answer = input('у вас id или screen name?(1 - id, 0 - screen name): ')
        if answer == '1':
            user_id = int(input('Введите ваш id: '))
            break
        elif answer == '0':
            screen_name = input('Введите ваш screen name: ')
            user_id = get_id_by_screen_name(screen_name, token_vk)
            print(f'Ваш id: {user_id}')
            break
        else:
            continue
    token_ya = input('Введите токен Яндекс полигон: ')
    count = int(input('Количество фото, которые нужно загрузить на Яндекс Диск: '))
    vk_1 = VkPhotoSaver(token_vk, user_id)
    ya_1 = YaDiskUpLoader(token_ya)
    ya_1.upload_photo_to_disk(vk_1.get_photo_info(count))
    command = input('Скачать фото на компьютер?(y/n)')
    if command == 'y':
        count = int(input('Количество фото, которые нужно загрузить на компьютер: '))
        vk_1.load_files(count)
        print('Работа завершена')
    else:
        print('Работа завершена')


if __name__ == '__main__':
    main()
