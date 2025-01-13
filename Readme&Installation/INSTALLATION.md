# WaterWise-AI: Installation Guide

## 🖥 Prerequisites

- Python 3.9+
- pip (Python Package Manager)
- Virtual Environment (recommended)

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/waterwise-ai.git
cd waterwise-ai
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

1. Create a `.env` file in the project root
2. Add necessary environment variables:

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_database_connection_string
```

### 5. Database Setup

```bash
flask db upgrade
```

### 6. Run the Application

```bash
flask run
```

## 🔧 Deployment Options

### Local Development
- Use `flask run` for local testing

### Production Deployment
- Use Gunicorn: `gunicorn app:app`
- Configure environment variables for production

## 🛠 Troubleshooting

### Common Installation Issues
- Ensure Python version compatibility
- Check virtual environment activation
- Verify all dependencies are installed

### Dependency Conflicts
- Use `pip freeze` to check installed packages
- Consider using `conda` for environment management

## 📦 Optional: Docker Deployment

```bash
docker build -t waterwise-ai .
docker run -p 5000:5000 waterwise-ai
```

## 🤝 Contributing

Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License.
