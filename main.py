import yandex_api
import vk_api
import aux_module


def main():
    token_vk = input('Введите токен доступа ВК: ')
    while True:
        answer = input('у вас id или screen name?(1 - id, 0 - screen name): ')
        if answer == '1':
            user_id = int(input('Введите ваш id: '))
            break
        elif answer == '0':
            screen_name = input('Введите ваш screen name: ')
            user_id = aux_module.get_id_by_screen_name(screen_name, token_vk)
            print(f'Ваш id: {user_id}')
            break
        else:
            continue
    token_ya = input('Введите токен Яндекс полигон: ')
    count = int(input('Количество фото, которые нужно загрузить на Яндекс Диск: '))
    vk_1 = vk_api.VkPhotoSaver(token_vk, user_id)
    ya_1 = yandex_api.YaDiskUpLoader(token_ya)
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
