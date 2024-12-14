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

# Danh sách các câu ngắn (tối đa 15 từ mỗi câu)
sentences = [
    "Hằng năm cứ vào cuối thu, lá ngoài đường rụng nhiều.",
    "Trên không có những đám mây bàng bạc, lòng tôi lại nao nức.",
    "Những kỷ niệm hoang mang của buổi tựu trường lại ùa về.",
    "Tôi không thể nào quên được những cảm giác trong sáng ấy.",
    "Chúng nảy nở trong lòng tôi như mấy cành hoa tươi.",
    "Như mỉm cười giữa bầu trời quang đãng, trong sáng và tươi đẹp.",
    "Những ý tưởng ấy tôi chưa lần nào ghi lên giấy.",
    "Vì hồi ấy tôi không biết ghi và ngày nay tôi không nhớ hết.",
    "Nhưng mỗi lần thấy mấy em nhỏ rụt rè núp dưới nón mẹ.",
    "Lần đầu tiên đến trường, lòng tôi lại tưng bừng rộn rã.",
    "Buổi sáng mai hôm ấy, một buổi mai đầy sương thu và gió lạnh.",
    "Mẹ tôi âu yếm nắm tay tôi dẫn đi trên con đường làng dài.",
    "Con đường này tôi đã quen đi lại lắm lần, nhưng lần này tôi thấy lạ.",
    "Cảnh vật chung quanh tôi đều thay đổi, vì chính lòng tôi đang thay đổi.",
    "Hôm nay tôi đi học, cảm giác mới lạ và hồi hộp.",
    "Tôi không lội qua sông thả diều như thằng Quí nữa.",
    "Không ra đồng nô hò như thằng Sơn nữa.",
    "Trong chiếc áo vải dù đen dài tôi cảm thấy mình trang trọng và đứng đắn.",
    "Dọc đường tôi thấy mấy cậu nhỏ trạc bằng tôi, áo quần tươm tất.",
    "Nhí nhảnh gọi tên nhau hay trao sách vở cho nhau xem mà tôi thèm.",
    "Hai quyển vở mới đang ở trên tay tôi đã bắt đầu thấy nặng.",
    "Tôi bặm tay ghì thật chặt, nhưng một quyển vở cũng chìa ra.",
    "Quyển vở chênh đầu chúi xuống đất, tôi xóc lên và nắm lại cẩn thận.",
    "Mấy cậu đi trước có sách vở thiệt nhiều lại kèm cả bút thước.",
    "Nhưng mấy cậu không để lộ vẻ khó khăn gì hết."
]

# Danh sách các câu ngắn (tối đa 15 từ mỗi câu) từ đoạn văn mới
sentences += [
    "Tôi muốn thử sức mình nên nhìn mẹ tôi.",
    "Mẹ đưa bút thước cho con cầm.",
    "Mẹ tôi cúi đầu nhìn tôi với cặp mắt thật âu yếm.",
    "Thôi để mẹ nắm cũng được.",
    "Tôi có ngay cái ý kiến vừa non nớt vừa ngây thơ này.",
    "Chắc chỉ người thạo mới cầm nổi bút thước.",
    "Ý nghĩ thoáng qua trong trí tôi nhẹ nhàng như một làn mây.",
    "Lướt ngang trên ngọn núi, ý nghĩ nhẹ nhàng và bay bổng.",
    "Trước sân trường làng Mỹ Lý đầy đặc cả người.",
    "Người nào áo quần cũng sạch sẽ, gương mặt cũng vui tươi và sáng sủa.",
    "Trước đó mấy hôm, lúc đi ngang làng Hòa An bẫy chim quyên với thằng Minh.",
    "Tôi có ghé trường một lần.",
    "Lần ấy trường đối với tôi là một nơi xa lạ.",
    "Tôi đi chung quanh các lớp để nhìn qua cửa kính mấy bản đồ.",
    "Tôi không có cảm tưởng gì khác là nhà trường cao ráo sạch sẽ hơn các nhà trong làng.",
    "Nhưng lần này lại khác.",
    "Trước mặt tôi, trường Mỹ Lý vừa xinh xắn vừa oai nghiêm như cái đình Hòa Ấp.",
    "Sân nó rộng, mình nó cao hơn những buổi trưa hè đầy vắng lặng.",
    "Lòng tôi đâm ra lo sợ vẩn vơ.",
    "Cũng như tôi, mấy cậu học trò mới bỡ ngỡ đứng nép bên người thân.",
    "Chỉ dám nhìn một nửa hay dám đi từng bước nhẹ.",
    "Họ như con chim con đứng trên bờ tổ.",
    "Họ nhìn quãng trời rộng muốn bay, nhưng còn ngập ngừng e sợ.",
    "Họ thèm vụng và ước ao thầm được như những học trò cũ.",
    "Biết lớp, biết thầy để khỏi phải rụt rè trong cảnh lạ.",
    "Sau một hồi trống thúc vang dội cả lòng tôi, mấy người học trò cũ đến sắp hàng.",
    "Rồi đi vào lớp.",
    "Chung quanh những cậu bé vụng về lúng túng như tôi cả.",
    "Các cậu không đi.",
    "Các cậu chỉ theo sức mạnh kéo dìu các cậu tới trước.",
    "Nói các cậu không đứng lại càng đúng hơn nữa.",
    "Vì hai chân các cậu cứ dềnh dàng mãi.",
    "Hết co lên một chân, các cậu lại duỗi mạnh như đá một quả banh tưởng tượng.",
    "Chính lúc này toàn thân các cậu cũng đang run run theo nhịp bước rộn ràng trong các lớp."
]

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
