import os
import logging
from utils.intelligent_bill_analyzer import analyze_bill

def main():
    # Configure logging to show all details
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Find the most recent bill in the uploads directory
    uploads_dir = 'uploads'
    
    if not os.path.exists(uploads_dir):
        print(f"Error: {uploads_dir} directory does not exist!")
        return

    # List all files in uploads directory
    files = os.listdir(uploads_dir)
    
    if not files:
        print(f"No files found in {uploads_dir} directory!")
        return

    # Sort files by modification time, get the most recent
    files_with_path = [os.path.join(uploads_dir, f) for f in files]
    most_recent_file = max(files_with_path, key=os.path.getmtime)

    print(f"Analyzing bill: {most_recent_file}")

    try:
        # Analyze the bill
        result = analyze_bill(most_recent_file, log_level=logging.DEBUG)
        
        # Print detailed results
        print("\n--- Bill Analysis Results ---")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success', False):
            print("\nParsed Details:")
            for key, value in result.get('parsed_details', {}).items():
                print(f"  {key.capitalize()}: {value}")
            
            print("\nBill Insights:")
            insights = result.get('bill_insights', {})
            for category, details in insights.items():
                print(f"\n{category.capitalize()}:")
                if isinstance(details, dict):
                    for key, value in details.items():
                        print(f"  {key.capitalize()}: {value}")
                else:
                    print(f"  {details}")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Unexpected error during bill analysis: {e}")

if __name__ == "__main__":
    main()
