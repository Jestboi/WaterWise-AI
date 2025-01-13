import os

# Create uploads directory
uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(uploads_dir, exist_ok=True)
print(f"Created uploads directory: {uploads_dir}")
