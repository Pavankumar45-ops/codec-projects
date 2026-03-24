"""
Image Recognition System - Single File Application
Run this file and open http://localhost:5000 in your browser
"""

import os
import uuid
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from PIL import Image

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load the AI model
print("Loading AI model... This may take a moment on first run.")
model = MobileNetV2(weights='imagenet')
print("Model loaded successfully! Ready to recognize images.")

def allowed_file(filename):
    """Check if file type is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(image_path):
    """Analyze image and return predictions"""
    try:
        # Open and prepare image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to model's required size
        img = img.resize((224, 224))
        
        # Convert to array for model
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Make prediction
        predictions = model.predict(img_array)
        
        # Get top 5 predictions
        results = decode_predictions(predictions, top=5)[0]
        
        # Format results nicely
        formatted_results = []
        for _, label, confidence in results:
            formatted_results.append({
                'label': label,
                'confidence': f"{confidence * 100:.2f}%",
                'confidence_score': float(confidence)
            })
        
        return formatted_results
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Web Routes
@app.route('/')
def home():
    """Home page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Recognition System</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            
            h1 {
                text-align: center;
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }
            
            .upload-area {
                border: 2px dashed #667eea;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                background: #f8f9ff;
            }
            
            .upload-area:hover {
                background: #f0f2ff;
                border-color: #764ba2;
            }
            
            .upload-icon {
                font-size: 48px;
                margin-bottom: 10px;
            }
            
            .upload-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 15px;
            }
            
            .upload-btn:hover {
                transform: scale(1.05);
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                display: none;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .results {
                display: none;
                margin-top: 30px;
            }
            
            .result-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
            }
            
            .preview img {
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .prediction-item {
                background: #f8f9fa;
                margin: 10px 0;
                padding: 15px;
                border-radius: 10px;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            .prediction-label {
                font-weight: bold;
                color: #333;
                margin-bottom: 8px;
                font-size: 16px;
            }
            
            .confidence-bar {
                background: #e0e0e0;
                border-radius: 10px;
                height: 8px;
                overflow: hidden;
                margin: 8px 0;
            }
            
            .confidence-fill {
                background: linear-gradient(90deg, #667eea, #764ba2);
                height: 100%;
                border-radius: 10px;
                transition: width 0.5s ease;
            }
            
            .confidence-text {
                font-size: 14px;
                color: #666;
            }
            
            .reset-btn {
                background: #f0f0f0;
                color: #666;
                border: none;
                padding: 10px 30px;
                border-radius: 25px;
                cursor: pointer;
                margin-top: 30px;
                width: 100%;
                font-size: 16px;
            }
            
            .reset-btn:hover {
                background: #e0e0e0;
            }
            
            .error {
                background: #f44336;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                display: none;
                text-align: center;
            }
            
            @media (max-width: 768px) {
                .result-container {
                    grid-template-columns: 1fr;
                }
                .container {
                    padding: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Image Recognition System</h1>
            <p class="subtitle">Upload any image and AI will identify what's in it</p>
            
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📸</div>
                <h3>Click or Drag & Drop to Upload</h3>
                <p>Supports: PNG, JPG, JPEG, GIF, BMP (Max 16MB)</p>
                <input type="file" id="fileInput" accept="image/*" style="display: none">
                <button class="upload-btn">Choose Image</button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing your image...</p>
            </div>
            
            <div class="results" id="results">
                <div class="result-container">
                    <div class="preview">
                        <h3>Your Image</h3>
                        <img id="previewImage" alt="Preview">
                    </div>
                    <div class="predictions">
                        <h3>What AI Sees</h3>
                        <div id="predictionsList"></div>
                    </div>
                </div>
                <button class="reset-btn" onclick="resetForm()">Analyze Another Image</button>
            </div>
            
            <div class="error" id="error"></div>
        </div>
        
        <script>
            const fileInput = document.getElementById('fileInput');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const error = document.getElementById('error');
            const previewImage = document.getElementById('previewImage');
            const predictionsList = document.getElementById('predictionsList');
            
            fileInput.addEventListener('change', function(e) {
                if (e.target.files[0]) {
                    uploadImage(e.target.files[0]);
                }
            });
            
            // Drag and drop
            const uploadArea = document.querySelector('.upload-area');
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.background = '#e8eaff';
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.background = '#f8f9ff';
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.background = '#f8f9ff';
                const file = e.dataTransfer.files[0];
                if (file && file.type.startsWith('image/')) {
                    uploadImage(file);
                } else {
                    showError('Please upload an image file');
                }
            });
            
            function uploadImage(file) {
                // Hide previous results
                results.style.display = 'none';
                error.style.display = 'none';
                
                // Show loading
                loading.style.display = 'block';
                document.querySelector('.upload-area').style.opacity = '0.5';
                
                const formData = new FormData();
                formData.append('image', file);
                
                fetch('/predict', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';
                    document.querySelector('.upload-area').style.opacity = '1';
                    
                    if (data.success) {
                        displayResults(data);
                    } else {
                        showError(data.error || 'Error processing image');
                    }
                })
                .catch(err => {
                    loading.style.display = 'none';
                    document.querySelector('.upload-area').style.opacity = '1';
                    showError('Network error. Please try again.');
                });
            }
            
            function displayResults(data) {
                // Show preview
                previewImage.src = data.image_url;
                
                // Clear and add predictions
                predictionsList.innerHTML = '';
                data.predictions.forEach((pred, index) => {
                    const confidencePercent = pred.confidence_score * 100;
                    const predDiv = document.createElement('div');
                    predDiv.className = 'prediction-item';
                    predDiv.innerHTML = `
                        <div class="prediction-label">${index + 1}. ${pred.label}</div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                        </div>
                        <div class="confidence-text">${pred.confidence}</div>
                    `;
                    predictionsList.appendChild(predDiv);
                });
                
                // Show results
                results.style.display = 'block';
                results.scrollIntoView({ behavior: 'smooth' });
            }
            
            function showError(message) {
                error.textContent = message;
                error.style.display = 'block';
                setTimeout(() => {
                    error.style.display = 'none';
                }, 5000);
            }
            
            function resetForm() {
                results.style.display = 'none';
                fileInput.value = '';
                previewImage.src = '';
                predictionsList.innerHTML = '';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/predict', methods=['POST'])
def predict():
    """Handle image upload and return predictions"""
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, GIF, or BMP'}), 400
        
        # Save file with unique name
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get predictions
        predictions = predict_image(filepath)
        
        if predictions is None:
            return jsonify({'error': 'Error analyzing image'}), 500
        
        # Return results
        return jsonify({
            'success': True,
            'image_url': f'/uploads/{filename}',
            'predictions': predictions
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Server error'}), 500

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Image Recognition System Started!")
    print("Open your browser and go to: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)