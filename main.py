import os
import json
import shutil
import requests

# Функция для скачивания файла по URL
def download_file(url, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    file_name = os.path.join(dest_folder, url.split("/")[-1])
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_name, "wb") as file:
            shutil.copyfileobj(response.raw, file)
        print(f"Скачан: {file_name}")
    else:
        print(f"Ошибка при скачивании: {url}")
    return file_name

# Чтение и парсинг JSON файла модпака
def parse_modpack_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        modpack_data = json.load(f)
    mods = modpack_data.get("files", [])
    return mods

# Скачивание модов с Modrinth
def download_mods(mods, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for mod in mods:
        project_id = mod.get("projectID")
        file_id = mod.get("fileID")
        if project_id and file_id:
            # Используем API Modrinth для получения информации о файле
            url = f"https://api.modrinth.com/v2/project/{project_id}/version/{file_id}"
            response = requests.get(url)
            if response.status_code == 200:
                version_data = response.json()
                download_url = version_data.get("files", [])[0].get("url")
                if download_url:
                    download_file(download_url, output_folder)
                else:
                    print(f"Не удалось найти URL для проекта {project_id}")
            else:
                print(f"Ошибка при запросе Modrinth API для {project_id}")

# Копирование папок из modpack в выходную папку
def copy_folders(source_folder, dest_folder):
    if os.path.exists(source_folder):
        for item in os.listdir(source_folder):
            src_path = os.path.join(source_folder, item)
            dest_path = os.path.join(dest_folder, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                print(f"Скопирована папка: {src_path} -> {dest_path}")
            else:
                shutil.copy2(src_path, dest_path)
                print(f"Скопирован файл: {src_path} -> {dest_path}")

# Основная функция
def main():
    json_path = "modpack.json"  # Путь к JSON файлу модпака
    output_folder = "compiled_modpack"  # Папка для сборки
    source_folder = "modpack/overrides"  # Папка с дополнительными файлами

    print("Парсим JSON файл...")
    mods = parse_modpack_json(json_path)

    print("Скачиваем моды...")
    mods_folder = os.path.join(output_folder, "mods")
    download_mods(mods, mods_folder)

    print("Копируем дополнительные файлы...")
    copy_folders(source_folder, output_folder)

    print("Сборка завершена!")

if __name__ == "__main__":
    main()
