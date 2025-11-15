#!/usr/bin/env python3
"""
Минимальный прототип визуализатора графа зависимостей пакетов
Этап 1: Конфигурация и базовое CLI
"""

import json
import os
import sys
import argparse
from urllib.parse import urlparse
from typing import Dict, Any

def load_configuration(config_file: str = "config.json") -> Dict[str, Any]:
    
    try:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Конфигурационный файл '{config_file}' не найден")
        
        with open(config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
            
        return config
        
    except FileNotFoundError as e:
        raise e
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка парсинга JSON в файле '{config_file}': {e}")
    except Exception as e:
        raise RuntimeError(f"Неожиданная ошибка при загрузке конфигурации: {e}")

def validate_configuration(config: Dict[str, Any]) -> None:
    
    required_params = ["package_name", "repository_url", "test_repository_mode", "output_filename", "ascii_tree_output"]
    
    for param in required_params:
        if param not in config:
            raise ValueError(f"Отсутствует обязательный параметр: {param}")
    
    if not isinstance(config["package_name"], str) or not config["package_name"].strip():
        raise ValueError("Имя пакета должно быть непустой строкой")
    
    if config["test_repository_mode"]:
        if "test_repository_path" not in config:
            raise ValueError("В режиме тестового репозитория должен быть указан test_repository_path")
    else:
        url = config["repository_url"]
        if not isinstance(url, str) or not url.strip():
            raise ValueError("URL репозитория должен быть непустой строкой")

def create_default_config(config_file: str = "config.json") -> None:
    
    default_config = {
        "package_name": "example-package",
        "repository_url": "https://github.com/example/repo",
        "test_repository_mode": False,
        "test_repository_path": "./test-repo",
        "output_filename": "dependency_graph.png",
        "ascii_tree_output": True,
        "package_filter": ""
    }
    
    with open(config_file, 'w', encoding='utf-8') as file:
        json.dump(default_config, file, indent=4, ensure_ascii=False)
    print(f"Создан файл конфигурации по умолчанию: {config_file}")

def merge_configs(file_config: Dict[str, Any], cli_args: argparse.Namespace) -> Dict[str, Any]:
   
    config = file_config.copy()
   
    if cli_args.package_name:
        config["package_name"] = cli_args.package_name
    if cli_args.repository_url:
        config["repository_url"] = cli_args.repository_url
    if cli_args.output_filename:
        config["output_filename"] = cli_args.output_filename
    if cli_args.package_filter is not None: 
        config["package_filter"] = cli_args.package_filter
    
  
    if cli_args.ascii_tree:
        config["ascii_tree_output"] = True
    if cli_args.no_ascii_tree:
        config["ascii_tree_output"] = False
    if cli_args.test_mode:
        config["test_repository_mode"] = True
    if cli_args.no_test_mode:
        config["test_repository_mode"] = False
    
    return config

def display_config_parameters(config: Dict[str, Any]) -> None:
    print("=== Конфигурационные параметры ===")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("==================================")

def setup_cli_parser() -> argparse.ArgumentParser:
    
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов - Этап 1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py --create-config          # Создать конфиг по умолчанию
  python main.py --config myconfig.json   # Использовать свой конфиг
  python main.py --package-name "react"   # Переопределить имя пакета
  python main.py --ascii-tree --no-test-mode  # Комбинировать флаги
        """
    )
    
    
    parser.add_argument("--config", default="config.json", help="Путь к конфигурационному файлу (по умолчанию: config.json)")
    parser.add_argument("--create-config", action="store_true", help="Создать конфигурационный файл по умолчанию и выйти")
    
    
    parser.add_argument("--package-name", help="Имя анализируемого пакета")
    parser.add_argument("--repository-url", help="URL репозитория пакетов")
    parser.add_argument("--output-filename", help="Имя файла для сохранения графа")
    parser.add_argument("--package-filter", help="Подстрока для фильтрации пакетов")
    
   
    ascii_group = parser.add_mutually_exclusive_group()
    ascii_group.add_argument("--ascii-tree", action="store_true", help="Включить вывод ASCII-дерева")
    ascii_group.add_argument("--no-ascii-tree", action="store_true", help="Выключить вывод ASCII-дерева")
    
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument("--test-mode", action="store_true", help="Включить режим тестового репозитория")
    test_group.add_argument("--no-test-mode", action="store_true", help="Выключить режим тестового репозитория")
    
    return parser

def main():
  
    parser = setup_cli_parser()
    args = parser.parse_args()
    
    if args.create_config:
        create_default_config(args.config)
        return
    
    try:
        
        file_config = load_configuration(args.config)
        
    
        config = merge_configs(file_config, args)
        
       
        validate_configuration(config)
        
        
        display_config_parameters(config)
        
       
        print(f"\n Конфигурация успешно загружена и валидирована!")
        print(f" Готов к анализу зависимостей пакета: {config['package_name']}")
        print(f" Результат будет сохранен в: {config['output_filename']}")
        if config['ascii_tree_output']:
            print(" ASCII-дерево зависимостей будет выведено")
        
    except FileNotFoundError:
        print(f" Ошибка: Конфигурационный файл '{args.config}' не найден.")
        print(" Создайте файл конфигурации: python main.py --create-config")
        sys.exit(1)
    except ValueError as e:
        print(f" Ошибка валидации конфигурации: {e}")
        sys.exit(1)
    except Exception as e:
        print(f" Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()