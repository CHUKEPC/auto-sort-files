#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт автосортировки файлов по типам
Автоматически сортирует файлы в указанной директории по категориям
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict
import argparse
from datetime import datetime


# Категории файлов и их расширения
FILE_CATEGORIES = {
    'Изображения': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif', '.heic', '.heif'],
    'Видео': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'],
    'Аудио': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.amr'],
    'Документы': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt', '.ods', '.odp'],
    'Архивы': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg'],
    'Программы': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.apk', '.app'],
    'Код': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs', '.ts', '.tsx', '.jsx', '.json', '.xml', '.yaml', '.yml'],
    'Таблицы': ['.csv', '.xls', '.xlsx', '.ods'],
    'Презентации': ['.ppt', '.pptx', '.odp', '.key'],
    'Другое': []  # Для файлов без известного расширения
}


def get_file_category(file_path):
    """
    Определяет категорию файла по его расширению
    """
    extension = Path(file_path).suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return 'Другое'


def create_category_folder(base_path, category):
    """
    Создает папку для категории, если её еще нет
    """
    category_path = base_path / category
    category_path.mkdir(exist_ok=True)
    return category_path


def move_file(source_path, destination_folder):
    """
    Перемещает файл в целевую папку
    Если файл с таким именем уже существует, добавляет номер
    """
    file_name = source_path.name
    destination_path = destination_folder / file_name

    # Если файл уже существует, добавляем номер
    counter = 1
    while destination_path.exists():
        stem = source_path.stem
        suffix = source_path.suffix
        new_name = f"{stem}_{counter}{suffix}"
        destination_path = destination_folder / new_name
        counter += 1

    shutil.move(str(source_path), str(destination_path))
    return destination_path


def sort_files(directory_path, dry_run=False, recursive=False):
    """
    Сортирует файлы в указанной директории

    Args:
        directory_path: Путь к директории для сортировки
        dry_run: Если True, только показывает что будет сделано, не перемещает файлы
        recursive: Если True, обрабатывает подпапки рекурсивно
    """
    directory = Path(directory_path)

    if not directory.exists():
        print(f"Ошибка: Директория '{directory_path}' не существует!")
        return

    if not directory.is_dir():
        print(f"Ошибка: '{directory_path}' не является директорией!")
        return

    # Статистика
    stats = defaultdict(int)
    moved_files = []
    errors = []

    # Получаем список файлов для обработки
    if recursive:
        files_to_process = [f for f in directory.rglob('*') if f.is_file() and f.parent != directory]
    else:
        files_to_process = [f for f in directory.iterdir() if f.is_file()]

    print(f"\n{'='*60}")
    print(f"Найдено файлов для обработки: {len(files_to_process)}")
    print(f"{'='*60}\n")

    if dry_run:
        print("РЕЖИМ ПРЕДПРОСМОТРА (dry-run) - файлы не будут перемещены\n")

    for file_path in files_to_process:
        try:
            # Пропускаем файлы в папках категорий
            if file_path.parent.name in FILE_CATEGORIES.keys():
                continue

            category = get_file_category(file_path)
            category_folder = create_category_folder(directory, category)

            if dry_run:
                print(f"[ПРЕДПРОСМОТР] {file_path.name} -> {category}/{file_path.name}")
            else:
                destination = move_file(file_path, category_folder)
                moved_files.append((file_path.name, category))
                print(f"✓ Перемещен: {file_path.name} -> {category}/")

            stats[category] += 1

        except Exception as e:
            error_msg = f"Ошибка при обработке {file_path.name}: {str(e)}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")

    # Выводим статистику
    print(f"\n{'='*60}")
    print("СТАТИСТИКА:")
    print(f"{'='*60}")
    for category, count in sorted(stats.items()):
        if count > 0:
            print(f"  {category}: {count} файл(ов)")

    if errors:
        print(f"\nОшибок: {len(errors)}")
        for error in errors:
            print(f"  - {error}")

    if dry_run:
        print(f"\nДля выполнения сортировки запустите скрипт без флага --dry-run")
    else:
        print(f"\n✓ Сортировка завершена! Обработано файлов: {sum(stats.values())}")


def main():
    parser = argparse.ArgumentParser(
        description='Автоматическая сортировка файлов по категориям',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python autosort.py                    # Сортировка текущей директории
  python autosort.py "C:\\Downloads"    # Сортировка указанной директории
  python autosort.py --dry-run           # Предпросмотр без перемещения файлов
  python autosort.py --recursive         # Рекурсивная обработка подпапок
        """
    )

    parser.add_argument(
        'directory',
        nargs='?',
        default=os.getcwd(),
        help='Директория для сортировки (по умолчанию: текущая директория)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Режим предпросмотра: показывает что будет сделано без перемещения файлов'
    )

    parser.add_argument(
        '--recursive',
        '-r',
        action='store_true',
        help='Рекурсивная обработка подпапок'
    )

    args = parser.parse_args()

    print("="*60)
    print("СКРИПТ АВТОСОРТИРОВКИ ФАЙЛОВ")
    print("="*60)
    print(f"Директория: {args.directory}")
    print(f"Режим предпросмотра: {'Да' if args.dry_run else 'Нет'}")
    print(f"Рекурсивная обработка: {'Да' if args.recursive else 'Нет'}")

    sort_files(args.directory, dry_run=args.dry_run, recursive=args.recursive)


if __name__ == '__main__':
    main()
