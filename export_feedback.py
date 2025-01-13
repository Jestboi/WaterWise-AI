import sqlite3
import json
import os
from datetime import datetime

def export_feedback_to_json():
    # Connect to the database
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    
    # Get all feedback entries
    c.execute('SELECT * FROM feedback')
    feedbacks = c.fetchall()
    
    # Convert to list of dictionaries
    feedback_list = []
    for feedback in feedbacks:
        feedback_dict = {
            'id': feedback[0],
            'name': feedback[1],
            'email': feedback[2],
            'subject': feedback[3],
            'message': feedback[4],
            'rating': feedback[5],
            'timestamp': feedback[6],
            'status': feedback[7]
        }
        feedback_list.append(feedback_dict)
    
    # Create dataset directory if it doesn't exist
    if not os.path.exists('dataset'):
        os.makedirs('dataset')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'dataset/feedback_export_{timestamp}.json'
    
    # Save to JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(feedback_list, f, indent=4, ensure_ascii=False)
    
    print(f"Exported {len(feedback_list)} feedback entries to {filename}")
    
    conn.close()
    return filename

if __name__ == '__main__':
    export_feedback_to_json()
