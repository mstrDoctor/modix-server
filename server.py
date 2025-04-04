from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Путь к папке с данными
DATA_FOLDER = 'data'

# Загрузка данных
def load_json(filename):
    try:
        with open(os.path.join(DATA_FOLDER, filename), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Сохранение данных
def save_json(filename, data):
    with open(os.path.join(DATA_FOLDER, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/comments/<file_id>', methods=['GET', 'POST'])
def comments(file_id):
    comments = load_json('comments.json')
    if request.method == 'GET':
        return jsonify(comments.get(file_id, []))
    else:
        data = request.json
        comments.setdefault(file_id, []).append({
            'name': data.get('name', 'Аноним'),
            'text': data.get('text', ''),
            'timestamp': int(os.times()[4] * 1000)
        })
        save_json('comments.json', comments)
        return jsonify({'status': 'ok'})

@app.route('/like/<file_id>', methods=['POST'])
def like(file_id):
    stats = load_json('stats.json')
    stats.setdefault(file_id, {'likes': 0, 'downloads': 0})
    stats[file_id]['likes'] += 1
    save_json('stats.json', stats)
    return jsonify({'likes': stats[file_id]['likes']})

@app.route('/stats/<file_id>', methods=['GET'])
def stats(file_id):
    stats = load_json('stats.json')
    file_stats = stats.get(file_id, {'likes': 0, 'downloads': 0})
    return jsonify(file_stats)

@app.route('/files/<file_id>', methods=['GET'])
def download(file_id):
    stats = load_json('stats.json')
    stats.setdefault(file_id, {'likes': 0, 'downloads': 0})
    stats[file_id]['downloads'] += 1
    save_json('stats.json', stats)
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
