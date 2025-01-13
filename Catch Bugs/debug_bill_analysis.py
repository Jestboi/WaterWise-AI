import os
import logging
from utils.intelligent_bill_analyzer import analyze_bill

def diagnose_bill_analysis():
    """
    Diagnostic script to test bill analysis functionality
    """
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bill_analysis_debug.log', mode='w'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('BillAnalysisDiagnostic')

    # Find uploads directory
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    
    if not os.path.exists(uploads_dir):
        logger.error(f"Uploads directory does not exist: {uploads_dir}")
        return

    # List all files in uploads directory
    try:
        files = os.listdir(uploads_dir)
        
        if not files:
            logger.warning(f"No files found in {uploads_dir}")
            return

        logger.info(f"Found {len(files)} files in uploads directory")
        
        # Analyze each file
        for filename in files:
            file_path = os.path.join(uploads_dir, filename)
            
            logger.info(f"\n--- Analyzing {filename} ---")
            
            # Check file extension
            _, ext = os.path.splitext(filename)
            if ext.lower() not in {'.pdf', '.jpg', '.jpeg', '.png', '.tiff'}:
                logger.warning(f"Unsupported file type: {ext}")
                continue

            # Perform bill analysis
            try:
                result = analyze_bill(file_path, log_level=logging.DEBUG)
                
                # Print detailed results
                logger.info("\nBill Analysis Results:")
                logger.info(f"Success: {result.get('success', False)}")
                
                if result.get('success', False):
                    logger.info("\nParsed Details:")
                    for key, value in result.get('parsed_details', {}).items():
                        logger.info(f"  {key.capitalize()}: {value}")
                    
                    logger.info("\nBill Insights:")
                    insights = result.get('bill_insights', {})
                    for category, details in insights.items():
                        logger.info(f"\n{category.capitalize()}:")
                        if isinstance(details, dict):
                            for key, value in details.items():
                                logger.info(f"  {key.capitalize()}: {value}")
                        else:
                            logger.info(f"  {details}")
                else:
                    logger.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                logger.error(f"Unexpected error analyzing {filename}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error processing uploads directory: {e}", exc_info=True)

if __name__ == "__main__":
    diagnose_bill_analysis()
