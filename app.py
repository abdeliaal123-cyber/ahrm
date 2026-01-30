from flask import Flask, request, jsonify, render_template
import cv2
import os
from deepface import DeepFace

app = Flask(__name__)

# المجلد الذي يحتوي على صور المستخدمين المقبولين فقط
AUTHORIZED_USERS_PATH = "authorized_users/"
if not os.path.exists(AUTHORIZED_USERS_PATH):
    os.makedirs(AUTHORIZED_USERS_PATH)

# --- وظيفة التحقق من الوجه والجنس ---
def verify_user(image_path):
    try:
        # 1. تحليل الصورة لمعرفة الجنس
        analysis = DeepFace.analyze(img_path=image_path, actions=['gender'], enforce_detection=True)
        gender = analysis[0]['dominant_gender']

        # 2. البحث عن تطابق الوجه في مجلد الأشخاص المقبولين (أنت من يضع الصور هناك)
        # سيقوم النظام بمقارنة الصورة المرفوعة بكل الصور في المجلد
        result = DeepFace.find(img_path=image_path, db_path=AUTHORIZED_USERS_PATH, enforce_detection=True)
        
        is_authorized = len(result[0]) > 0
        
        return is_authorized, gender
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return "واجهة تسجيل الدخول بالوجه (يتم ربطها بكاميرا الويب)"

@app.route('/login', methods=['POST'])
def login():
    if 'photo' not in request.files:
        return jsonify({"status": "error", "message": "لم يتم التقاط صورة"}), 400
    
    file = request.files['photo']
    temp_path = "temp_login.jpg"
    file.save(temp_path)

    authorized, gender_or_error = verify_user(temp_path)

    if authorized:
        return jsonify({
            "status": "success",
            "message": f"تم تسجيل الدخول بنجاح! الجنس: {gender_or_error}",
            "redirect": "/dashboard"
        })
    else:
        return jsonify({
            "status": "denied",
            "message": "عذراً، وجهك غير مسجل أو لم يتم قبولك من قبل المدير بعد."
        })

if __name__ == '__main__':
    app.run(debug=True)
