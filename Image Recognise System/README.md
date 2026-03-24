> Image Recognition System (Flask + MobileNetV2)

A simple yet powerful AI-based Image Recognition Web App built using Flask and TensorFlow (MobileNetV2). 
Upload any image, and the system will predict what’s inside it with confidence scores.

> Features
📸 Upload images (PNG, JPG, JPEG, GIF, BMP)
🤖 AI-powered image classification using MobileNetV2
📊 Top 5 predictions with confidence scores
🎨 Modern and responsive UI
⚡ Fast and lightweight single-file application
🖥️ Drag & Drop support
>
> Tech Stack
Backend: Flask (Python)
AI Model: TensorFlow / Keras (MobileNetV2)
Frontend: HTML, CSS, JavaScript
Image Processing: Pillow (PIL), NumPy
>
> How It Works
User uploads an image
Image is resized to 224x224
Preprocessing is applied using MobileNetV2 requirements
Model predicts probabilities
Top 5 predictions are displayed with confidence scores
>
> Configuration
Max file size: 16MB
Allowed formats: PNG, JPG, JPEG, GIF, BMP
Upload folder: uploads/
