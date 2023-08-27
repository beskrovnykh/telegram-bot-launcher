#!/usr/bin/env python3

import os
import subprocess
import argparse
import json
import signal
import urllib.request


from ngrok_wrapper import start_ngrok
from ngrok_wrapper import stop_ngrok
from ngrok_wrapper import check_ngrok_installed


def get_bot_token_from_config(stage="local"):
    """
    Получает токен бота из конфигурации Chalice для указанной стадии.

    Args:
        stage (str, optional): Стадия, для которой нужно получить токен. По умолчанию "local".

    Returns:
        str: Токен бота для указанной стадии.
    """
    config_path = '.chalice/config.json'
    
    # Проверка существования файла конфигурации
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Chalice configuration file '{config_path}' not found.")
    
    with open(config_path, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from {config_path}")

    # Проверка наличия необходимых ключей в конфигурации
    if "stages" not in config:
        raise KeyError("Key 'stages' not found in Chalice configuration.")
    if stage not in config["stages"]:
        raise KeyError(f"Stage '{stage}' not found in Chalice configuration.")
    if "environment_variables" not in config["stages"][stage]:
        raise KeyError(f"Key 'environment_variables' not found for stage '{stage}' in Chalice configuration.")
    if "TELEGRAM_BOT_ID" not in config["stages"][stage]["environment_variables"]:
        raise KeyError(f"TELEGRAM_BOT_ID not found for stage '{stage}' in Chalice configuration.")

    return config["stages"][stage]["environment_variables"]["TELEGRAM_BOT_ID"]


def set_telegram_webhook(telegram_bot_id, webhook_url):
    """
    Устанавливает вебхук для Telegram бота.

    Args:
        telegram_bot_id (str): ID бота Telegram.
        webhook_url (str): URL вебхука, который нужно установить.

    Returns:
        dict: Ответ от Telegram API после установки вебхука.
    """
    url = f"https://api.telegram.org/bot{telegram_bot_id}/setWebhook"
    data = json.dumps({"url": webhook_url}).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Python-urllib/3.x"  # Некоторые сервисы блокируют запросы без User-Agent, поэтому добавим его
    }

    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(request) as response:
            response_data = json.loads(response.read().decode())

            # Проверка ответа от Telegram API
            if response_data.get('ok'):
                print("Webhook successfully set!")
            else:
                print(f"Failed to set webhook. Error: {response_data.get('description')}")
                
            return response_data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")

def launch_bot(port, stage, venv_path, no_autoreload):

    """
    Запускает бота локально, используя ngrok для обработки вебхуков из Telegram.

    :param port: Порт, на котором будет запущен локальный сервер Chalice.
    :param stage: Стадия разработки (обычно "local" или "prod").
    :param venv_path: Путь к виртуальной среде Python.
    :param no_autoreload: Если True, то сервер Chalice не будет автоматически перезагружаться при изменении кода.
    """

    def stop_server(signum, frame):
        if server_process:
            stop_ngrok()
            server_process.terminate()
    
    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)
    # Запускаем ngrok
    ngrok_url = start_ngrok(port)
    if not ngrok_url:
        print("Failed to start ngrok.")
    else:
        print(f"Ngrok URL: {ngrok_url}")

    # Устанавливаем переменные окружения
    os.environ["WEBHOOK_BASE_URL"] = ngrok_url

    # Запускаем chalice local
    activate_venv_cmd = f"source {venv_path}/bin/activate"
    chalice_cmd = f"chalice local --port {port} --stage {stage}"

    if no_autoreload:
        chalice_cmd += " --no-autoreload"

    full_cmd = f"{activate_venv_cmd} && {chalice_cmd}"
    server_process = subprocess.Popen(full_cmd, shell=True)

    try:
        telegram_bot_id = get_bot_token_from_config("local")
        print(f"Telegram Bot: {telegram_bot_id}")
        set_telegram_webhook(telegram_bot_id=telegram_bot_id, webhook_url=f"{ngrok_url}/webhook")
    except Exception as e:
        print(f"Error: {e}")

    server_process.wait()


if __name__ == "__main__":

    # Проверка на наличие установленного ngrok
    if not check_ngrok_installed():
        print("Error: ngrok не установлен. Установите ngrok для продолжения.")
        exit(1)

    # Инициализация парсера аргументов
    parser = argparse.ArgumentParser(description="Launch bot with ngrok.")

    # Порт, на котором запущено приложение Chalice
    parser.add_argument('--port', type=int, default=8000, help="The port on which the Chalice app is running.")

    # Стадия Chalice для использования (например, "local", "dev", "prod")
    parser.add_argument('--stage', default="local", help="The stage for Chalice to use.")

    # Путь к виртуальному окружению Python
    parser.add_argument('--venv', default=".venv", help="Path to the virtual environment.")

    # Отключить авто-перезагрузчик в Chalice
    parser.add_argument('--no-autoreload', action='store_true', help="Disable the auto-reloader in Chalice.")

    # Разбор аргументов и запуск бота
    args = parser.parse_args()
    launch_bot(args.port, args.stage, args.venv, args.no_autoreload)
