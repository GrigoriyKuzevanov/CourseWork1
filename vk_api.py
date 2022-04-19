import requests
import os
from progress.bar import IncrementalBar
import aux_module


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
            res = (aux_module.max_size(item['sizes']))
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
                    with open(aux_module.path_builder(file['likes']), 'wb') as f:
                        f.write(resp.content)
                    name = file['likes']
                else:
                    with open(aux_module.path_builder(file['upload_date']), 'wb') as f:
                        f.write(resp.content)
                bar.next()
            else:
                print(f'Ошибка загрузки, статус ответа: {resp.status_code}')
        bar.finish()
        print(f'Загрузка на компьютер завершена')
