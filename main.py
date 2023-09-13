import subprocess
import logging
import time
import sys
import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

SERVERS_DIR = str(os.getenv('MC_SERVERS_DIR'))
if not os.path.isdir(SERVERS_DIR):
    sys.exit(f"SERVERS_DIR: ({SERVERS_DIR}) doesn't exist or is not a directory")

app = Flask(__name__)

@app.route('/list', methods=['GET'])
def list():
    try:
        items = os.listdir(SERVERS_DIR)
        directories = [item for item in items if os.path.isdir(os.path.join(SERVERS_DIR, item))]
        return jsonify({'message': directories})
    except Exception:
        return jsonify({'error': 'Error listing servers'}), 500

@app.route('/start', methods=['POST'])
def start():
    server = request.json.get('server')
    try:
        # Run the 'docker-compose up' command to start the stack
        subprocess.Popen(['docker-compose', '-f', f'{SERVERS_DIR}/{server}/docker-compose.yml', 'up', '-d'])
        return jsonify({'message': f'Started {server}'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr.decode()}), 500

@app.route('/stop', methods=['POST'])
def stop():
    server = request.json.get('server')
    try:
        subprocess.Popen(['docker-compose', '-f', f'{SERVERS_DIR}/{server}/docker-compose.yml', 'down', '-v', '--remove-orphans'])
        return jsonify({'message': f'Stopped {server}'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr.decode()}), 500

def read_existing_time(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                time = int(file.read().strip())
                logging.debug(f"Read timefile, time: {time}")
                return time
            except ValueError:
                pass
    else:
        logging.debug("No timefile to read")
    return None

def update_timefile(file_path, new_time):
    existing_time = read_existing_time(file_path)

    # Only update time if it is greater than what is present in the file
    if existing_time is None or new_time > existing_time:
        directory_path = os.path.dirname(file_path)
        os.makedirs(directory_path, exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(str(new_time))
            logging.info(f"Updated time in {file_path} to {new_time}")

@app.route('/extendtime', methods=['POST'])
def extendtime():
    server = request.json.get('server')
    days = request.json.get('days')
    seconds = int(days) * 86400
    timefile = f'/data/{server}/timefile'
    server_dir = f'{SERVERS_DIR}/{server}/data'

    try:
        update_timefile(timefile, int(time.time()) + seconds)

        dirs = [d for d in os.listdir(server_dir) if os.path.isdir(os.path.join(server_dir,d))]
        for dir in dirs:
            # https://docker-minecraft-server.readthedocs.io/en/latest/misc/autopause-autostop/autostop/
            skipfile = os.path.join(server_dir, dir, '.skipfile')
            logging.info(f"Adding skipfile {skipfile}")
            with open(skipfile, "w"):
                pass

        return jsonify({'message': f'Extended time for {server} another {days} days'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr.decode()}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

