from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
import os
import uuid
import zipfile
from io import BytesIO
import csv
import shutil

app = Flask(__name__)
CORS(app)

# Đường dẫn lưu trữ các file audio
AUDIO_FOLDER = 'static/audio/'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# File chứa dữ liệu các câu cần đọc
SENTENCE_FILE = 'static/vi_VN/0000000001_0300000050_General.txt'

# Danh sách các câu ngắn
sentences = []

def load_sentences():
    """Load sentences from the text file."""
    global sentences
    if os.path.exists(SENTENCE_FILE):
        with open(SENTENCE_FILE, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                # Split each line into sentence id and sentence content
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    sentences.append(parts[1])  # Add only the sentence content
    else:
        print(f"File {SENTENCE_FILE} does not exist.")

# Load sentences when the application starts
load_sentences()

# Dictionary to store the current sentence index for each user
user_progress = {}

@app.route('/')
def index():
    return render_template('index.html', sentences=sentences)

@app.route('/get-next-sentence/<user_id>', methods=['GET'])
def get_next_sentence(user_id):
    # Get the current sentence index for the user, default to 0 if not set
    current_index = user_progress.get(user_id, 0)

    if current_index < len(sentences):
        sentence = sentences[current_index]
        user_progress[user_id] = current_index + 1  # Update to the next sentence index
        return jsonify({'sentence': sentence, 'index': current_index + 1})
    else:
        return jsonify({'message': 'Tất cả các câu đã hoàn thành!'}), 404

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    audio = request.files['audio']
    sentence_index = int(request.form['sentence_index'])
    user_id = request.form['user_id']
    user_folder = os.path.join(AUDIO_FOLDER, user_id)
    
    # Ensure user folder exists
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    audio_filename = f"{uuid.uuid4().hex}.wav"
    audio_path = os.path.join(user_folder, audio_filename)
    
    # Save audio file
    audio.save(audio_path)

    # Ghi thông tin vào file metadata.csv
    metadata_path = f'{user_folder}/metadata.csv'
    with open(metadata_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow([audio_filename, sentences[sentence_index]])

    return jsonify({'message': 'Audio uploaded successfully'}), 200

@app.route('/download-zip/<user_id>', methods=['GET'])
def download_zip(user_id):
    user_folder = os.path.join(AUDIO_FOLDER, user_id)
    if not os.path.exists(user_folder):
        return jsonify({'message': 'User data not found'}), 404

    zip_filename = f'{user_id}_audio_files.zip'
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add audio files
        for filename in os.listdir(user_folder):
            if filename.endswith('.wav'):
                zip_file.write(os.path.join(user_folder, filename), arcname=filename)

        # Add metadata.csv for the specific user
        metadata_path = os.path.join(user_folder, 'metadata.csv')
        zip_file.write(metadata_path, arcname='metadata.csv')

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=zip_filename, mimetype='application/zip')

@app.route('/reset-all/<user_id>', methods=['POST'])
def reset_all(user_id):
    # Only delete the user's folder
    user_folder_path = os.path.join(AUDIO_FOLDER, user_id)
    if os.path.exists(user_folder_path):
        shutil.rmtree(user_folder_path)
        return jsonify({'message': f'Data for user {user_id} has been reset!'}), 200
    else:
        return jsonify({'message': f'No data found for user {user_id}'}), 404

if __name__ == '__main__':
    app.run(debug=True)
