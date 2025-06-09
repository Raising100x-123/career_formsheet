from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()

# Configure MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['career_db']
collection = db['applications']

# Configure Upload Folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('form.html')  # Serve form.html from templates folder

@app.route('/submit_application', methods=['POST'])
def submit_application():
    category = request.form.get('category')
    position = request.form.get('position')
    email = request.form.get('email')
    mobile = request.form.get('mobile')

    if 'resume' not in request.files:
        return jsonify({'error': 'No resume uploaded'}), 400

    resume = request.files['resume']

    if resume and allowed_file(resume.filename):
        filename = secure_filename(resume.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(filepath)

        # Insert into MongoDB
        collection.insert_one({
            'category': category,
            'position': position,
            'email': email,
            'mobile': mobile,
            'resume_path': filepath
        })

        return jsonify({'message': 'Application submitted successfully!'}), 200
    else:
        return jsonify({'error': 'Invalid file type. Only PDF allowed.'}), 400

if __name__ == '__main__':
    import os
    
    app.run(host='0.0.0.0', port=8000)
