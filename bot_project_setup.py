#!/usr/bin/env python3
import json
import os
import argparse

TEMPLATE_APP_PY = """
import os
from chalice import Chalice
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

app = Chalice(app_name='{app_name}')

bot_token = os.environ["TELEGRAM_BOT_ID"]
updater = Updater(token=bot_token, use_context=True)

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я ваш бот.")

start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler)

@app.route('/webhook', methods=['POST'])
def webhook():
    if app.current_request.json_body:
        update = Update.de_json(app.current_request.json_body, updater.bot)
        updater.dispatcher.process_update(update)
    return {{}}
"""


def generate_app_file(app_name, project_dir):
    """
    Generates the main app.py file for the bot project.

    Args:
        app_name (str): The name of the bot project.
        project_dir (str): The directory where the project files are to be generated.
    """
    content = TEMPLATE_APP_PY.format(app_name=app_name)
    with open(os.path.join(project_dir, 'app.py'), 'w') as f:
        f.write(content)


def generate_policy_file(project_dir):
    """
    Generates the IAM policy file (dev-policy.json) for the bot project.

    Args:
        project_dir (str): The directory where the policy file is to be generated.
    """
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "cloudwatch:PutMetricData"
                ],
                "Resource": [
                    "arn:*:logs:*:*:*",
                    "arn:*:cloudwatch:*:*:*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:*",
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": "*"
            }
        ]
    }

    chalice_dir = os.path.join(project_dir, '.chalice')
    if not os.path.exists(chalice_dir):
        os.makedirs(chalice_dir)

    policy_file_path = os.path.join(project_dir, '.chalice', 'dev-policy.json')

    with open(policy_file_path, 'w') as f:
        json.dump(policy, f, indent=4)


def generate_chalice_config(project_dir, project_name, bot_token):
    """
    Generates the Chalice configuration file for the bot project.

    Args:
        project_dir (str): The directory where the config file is to be generated.
        project_name (str): The name of the bot project.
        bot_token (str): The Telegram bot token for local development.
    """
    chalice_dir = os.path.join(project_dir, '.chalice')
    os.makedirs(chalice_dir, exist_ok=True)

    config_data = {
        "version": "2.0",
        "app_name": project_name,
        "stages": {
            "local": {
                "iam_policy_file": "dev-policy.json",
                "api_gateway_stage": "api",
                "autogen_policy": False,
                "environment_variables": {
                    "TELEGRAM_BOT_ID": bot_token
                }
            },
            "dev": {
                "iam_policy_file": "dev-policy.json",
                "api_gateway_stage": "api",
                "autogen_policy": False,
                "environment_variables": {
                    "TELEGRAM_BOT_ID": "YOUR_BOT_TOKEN_HERE"
                }
            }
        }
    }

    with open(os.path.join(chalice_dir, 'config.json'), 'w') as f:
        json.dump(config_data, f, indent=4)


def generate_requirements(project_dir, dependencies):
    """
    Generates the requirements.txt file for the bot project.

    Args:
        project_dir (str): The directory where the requirements file is to be generated.
        dependencies (list): A list of additional dependencies to be added.
    """
    with open(os.path.join(project_dir, 'requirements.txt'), 'w') as f:
        f.write('chalice\n')
        f.write('python-telegram-bot==13.11\n')
        for dependency in dependencies:
            f.write(f"{dependency}\n")


def generate_project(project_name, bot_token, dependencies):
    """
    Orchestrates the generation of the entire bot project.

    Args:
        project_name (str): The name of the bot project.
        bot_token (str): The Telegram bot token for local development.
        dependencies (list): A list of additional dependencies to be added.
    """
    # Create the main project directory
    project_dir = os.path.join(os.getcwd(), project_name)
    os.makedirs(project_dir, exist_ok=True)

    # Generate app.py
    generate_app_file(project_name, project_dir)

    # Generate .chalice/config.json
    generate_chalice_config(project_dir, project_name, bot_token)

    # Generate dev-policy.json
    generate_policy_file(project_dir)

    # Generate requirements.txt
    generate_requirements(project_dir, dependencies)

    print(f"Project {project_name} has been successfully created.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a bot project.")

    parser.add_argument('project_name', type=str, help='Name of the project to be generated.')
    parser.add_argument('bot_token', type=str, help='Telegram bot token for local development.')
    parser.add_argument('--dependencies', nargs='*', default=[],
                        help='Additional dependencies to include in requirements.txt (e.g. openai).')

    args = parser.parse_args()

    generate_project(args.project_name, args.bot_token, args.dependencies)
