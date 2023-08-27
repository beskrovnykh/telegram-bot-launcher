import os
import subprocess
import json
import time
import argparse

ngrok_process = None  # глобальная переменная для хранения экземпляра процесса ngrok


def get_ngrok_url():
    try:
        response = subprocess.check_output(['curl', '-s', 'http://localhost:4040/api/tunnels'])
        json_data = json.loads(response.decode('utf-8'))
        return json_data['tunnels'][0]['public_url']
    except Exception as e:
        print(f"Error getting ngrok URL: {e}")
        return None

def start_ngrok(port):
    global ngrok_process
    if ngrok_process:
        print("Ngrok is already running.")
        return None
    ngrok_process = subprocess.Popen(['ngrok', 'http', str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    return get_ngrok_url()

def stop_ngrok():
    global ngrok_process
    if ngrok_process:
        ngrok_process.terminate()
        ngrok_process = None
    print("Ngrok stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage ngrok process.")
    parser.add_argument('action', choices=['start', 'stop', 'get-url'], help="Action to perform: start, stop, or retrieve ngrok URL.")
    parser.add_argument('--port', type=int, default=8000, help="The port on which the Chalice app is running.")
    args = parser.parse_args()

    if args.action == "start":
        ngrok_url = start_ngrok(args.port)
        if ngrok_url:
            print(f"Ngrok started with URL: {ngrok_url}")
            os.environ["WEBHOOK_BASE_URL"] = ngrok_url
            print(f"WEBHOOK_BASE_URL set to: {os.environ['WEBHOOK_BASE_URL']}")

        else:
            print("Failed to start ngrok.")
    elif args.action == "stop":
        stop_ngrok()
    elif args.action == "get-url":
        url = get_ngrok_url()
        if url:
            print(f"Ngrok public URL: {url}")
        else:
            print("Failed to retrieve ngrok URL.")
