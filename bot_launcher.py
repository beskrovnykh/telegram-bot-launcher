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
    Gets the bot token from the Chalice configuration for the specified stage.

    Args:
        stage (str, optional): The stage for which to retrieve the bot token. Default is "local".

    Returns:
        str: The bot token for the specified stage.
    """
    config_path = '.chalice/config.json'

    # Check if the configuration file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Chalice configuration file '{config_path}' not found.")

    with open(config_path, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from {config_path}")

    # Check for the presence of required keys in the configuration
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
    Sets the webhook for the Telegram bot.

    Args:
        telegram_bot_id (str): The Telegram bot's ID.
        webhook_url (str): The URL of the webhook to set.

    Returns:
        dict: The response from the Telegram API after setting the webhook.
    """

    url = f"https://api.telegram.org/bot{telegram_bot_id}/setWebhook"
    data = json.dumps({"url": webhook_url}).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Python-urllib/3.x"  # Some services block requests without User-Agent, so we add it
    }

    request = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request) as response:
            response_data = json.loads(response.read().decode())

            # Check Telegram API response
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
    Launches the bot locally using ngrok to handle webhooks from Telegram.

    :param port: The port on which the local Chalice server will be running.
    :param stage: The development stage (usually "local" or "prod").
    :param venv_path: The path to the Python virtual environment.
    :param no_autoreload: If True, the Chalice server will not automatically reload on code changes.
    """

    def stop_server(signum, frame):
        if server_process:
            stop_ngrok()
            server_process.terminate()

    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)
    # Start ngrok
    ngrok_url = start_ngrok(port)
    if not ngrok_url:
        print("Failed to start ngrok.")
    else:
        print(f"Ngrok URL: {ngrok_url}")

    # Set environment variables
    os.environ["WEBHOOK_BASE_URL"] = ngrok_url

    # Launch Chalice locally
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

    # Check for the presence of installed ngrok
    if not check_ngrok_installed():
        print("Error: ngrok is not installed. Install ngrok to proceed.")
        exit(1)

    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Launch bot with ngrok.")

    # Port on which the Chalice application is running
    parser.add_argument('--port', type=int, default=8000, help="The port on which the Chalice app is running.")

    # Chalice stage to use (e.g., "local", "dev", "prod")
    parser.add_argument('--stage', default="local", help="The stage for Chalice to use.")

    # Path to Python virtual environment
    parser.add_argument('--venv', default=".venv", help="Path to the virtual environment.")

    # Disable auto-reloader in Chalice
    parser.add_argument('--no-autoreload', action='store_true', help="Disable the auto-reloader in Chalice.")

    # Parse arguments and launch the bot
    args = parser.parse_args()

    launch_bot(args.port, args.stage, args.venv, args.no_autoreload)