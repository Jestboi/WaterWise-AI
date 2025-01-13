# WaterWise-AI: Intelligent Water Management Platform

## 🌊 Project Overview

WaterWise-AI is an advanced, AI-powered platform designed to revolutionize water resource management through intelligent insights, predictive analytics, and sustainable solutions.

### 🚀 Key Features

- **AI-Driven Water Consumption Analysis**
- **Predictive Maintenance for Water Infrastructure**
- **Real-time Resource Optimization**
- **Personalized Water Conservation Recommendations**
- **Climate Impact Modeling**

## 🛠 Technology Stack

- **Backend**: Flask, Python
- **Frontend**: HTML5, Tailwind CSS
- **AI/ML**: TensorFlow, PyTorch, scikit-learn
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Plotly

## 🌍 Impact

WaterWise-AI contributes to:
- Sustainable water resource management
- Reducing water waste
- Supporting agricultural and urban water efficiency
- Climate change adaptation strategies

## 🏆 Awards & Recognition

- Climate Tech Innovation Award 2024
- Water Conservation Excellence Grant

## 📄 License

MIT License

## 🤝 Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for details.

## Features

- 🤖 AI-powered chatbot specialized in water conservation
- 🌊 Focus on Turkish water management and DSİ policies
- 📁 File upload and analysis capabilities
- 💬 Real-time chat interface with typing indicators
- 🌓 Dark/Light theme toggle
- 👥 Admin panel for feedback management
- 📊 Training data export functionality
- 🔒 Secure authentication system
- 💸 AWS-Powered Intelligent Water Tax Bill Analysis
- 🔍 Advanced OCR and Document Processing

## Prerequisites

- Python 3.12+
- Ollama (Local LLM server)
- SQLite3
- Modern web browser with JavaScript enabled
- At least 8GB RAM recommended for running the LLM

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd water-conservation-chatbot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install and start Ollama:
```bash
# Windows
# Download Ollama from https://ollama.ai/download
# Start Ollama service
ollama serve
```

4. Download the required model:
```bash
ollama pull water-expert
```

## Configuration

1. Environment Setup:
   - Copy `.env.example` to `.env`
   - Update the configuration values as needed
   - Make sure to set a secure SECRET_KEY

2. Network Access:
   - The application runs on `0.0.0.0:5000` by default
   - Accessible from local network at `http://<your-ip>:5000`
   - CSRF protection is relaxed for local network (197.***.* and 127.0.0.1)

3. Security Notes:
   - HTTPS is recommended for production deployment
   - Local network access has relaxed CSRF checks
   - Session cookies are HTTP-only
   - File upload size is limited to 16MB

## Network Access

1. Find your IP address:
```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
# or
ip addr
```

2. Access the application:
- Local access: Always available at `http://127.0.0.1:5000`
- Network access: Available at `http://<your-ip>:5000`
  - Example: `http://192.---.-.---:5000`

3. When changing networks:
- No code changes needed
- Just find your new IP address
- Access using the new IP address
- CSRF protection automatically works with any local network (192.168.*)

## Running the Application

1. Start the Ollama service:
```bash
ollama serve
```

2. Run the Flask application:
```bash
python app.py
```

3. Access the application:
   - Local: http://127.0.0.1:5000
   - Network: http://<your-ip>:5000

## Usage

### Chat Interface
- Real-time conversation with water conservation expert AI
- Typing indicators for better user experience
- Dark/Light theme toggle
- File upload and analysis
- Chat history persistence
- Creator response easter egg

### File Upload Features
- File size limits: 5 bytes to 50MB
- Supported formats: TXT, DOC, DOCX
- Content analysis and recommendations

### Admin Panel
- Secure authentication system
- Feedback management
- Training data export
- User interaction monitoring

### Technical Features
- CSRF protection with local network support
- Secure file upload handling
- SQLite database for data persistence
- Error logging and monitoring
- Responsive design for all devices

## Security Features

- CSRF Protection
- Secure Session Management
- HTTP-Only Cookies
- XSS Prevention
- Input Sanitization
- File Upload Validation

## Ollama Locations

1. Program Files:
   - Location: `C:\Users\<username>\AppData\Local\Programs\Ollama`
   - Contains: Executable files, libraries, and runners
   - Key files:
     - `ollama.exe` - Main executable
     - `lib/` - Libraries and dependencies

2. Model Files:
   - Location: `C:\Users\<username>\.ollama\models`
   - Contains: Downloaded models and their data
   - Structure:
     - `blobs/` - Model weights and large files
     - `manifests/` - Model configuration files

3. Model Management:
```bash
# List installed models and their sizes
ollama list

# Show model details
ollama show water-expert

# Pull/update model
ollama pull water-expert

# Remove model
ollama rm water-expert
```

## Model Location and Management

1. Model Storage Location:
   - Windows: `C:\Users\<username>\.ollama\models`
   - Linux: `~/.ollama/models`
   - Mac: `~/.ollama/models`

2. Model Files:
   - `blobs/` - Contains model weights and large files
   - `manifests/` - Contains model configuration files

3. Useful Commands:
```bash
# List all installed models
ollama list

# Show model details
ollama show water-expert

# Pull/update model
ollama pull water-expert

# Remove model
ollama rm water-expert
```

## Project Structure

```
water-conservation-chatbot/
├── app.py                 # Main Flask application
├── model_inference.py     # Chatbot model integration
├── download_model.py      # Model download script
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
├── templates/            # HTML templates
├── uploads/             # File upload directory
└── dataset/             # Training data
```

## Troubleshooting

### Common Issues

1. Ollama Service Not Running
   ```
   Error: Could not connect to Ollama service
   Solution: Ensure ollama serve is running
   ```

2. Database Errors
   ```
   Error: Database error
   Solution: Check file permissions and SQLite installation
   ```

3. File Upload Issues
   ```
   Error: File size/type not supported
   Solution: Verify file meets size (5B-50MB) and type requirements
   ```

### Debug Mode

For development, enable debug mode:
```python
app.run(debug=True)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Ollama team for the local LLM server
- Flask team for the web framework
- All contributors and users of the application

## Contact

[Add your contact information here]
