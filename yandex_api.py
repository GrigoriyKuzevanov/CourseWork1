import requests
from progress.bar import IncrementalBar
import aux_module


class YaDiskUpLoader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_dir(self):
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

    def upload_photo_to_disk(self, list_files):
        self.create_dir()
        data = []
        bar = IncrementalBar(' Загрузка файлов на Яндекс.диск', max=len(list_files))
        name = -1
        for file in list_files:
            file_info = dict()
            url = file['url']
            if file['likes'] != name:
                path = f"{'photos from VK'}/{file['likes']}.jpg"
                file_info['file_name'] = f"{file['likes']}.jpg"
            else:
                path = f"{'photos from VK'}/{file['upload_date']}.jpg"
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
        aux_module.data_to_json(data)
