import os
import sys
import logging

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from utils.intelligent_bill_analyzer import IntelligentBillAnalyzer

def test_water_bill_trends():
    """
    Test 6-month water bill trend analysis
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('water_bill_trends.log', mode='w'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('WaterBillTrendsTest')

    # Find uploads directory
    uploads_dir = os.path.join(project_dir, 'uploads')
    
    if not os.path.exists(uploads_dir):
        logger.error(f"Uploads directory does not exist: {uploads_dir}")
        return

    # List PDF files in uploads directory
    try:
        pdf_files = [
            os.path.join(uploads_dir, f) 
            for f in os.listdir(uploads_dir) 
            if f.lower().endswith('.pdf')
        ]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {uploads_dir}")
            return

        logger.info(f"Found {len(pdf_files)} PDF files")
        
        # Initialize analyzer
        analyzer = IntelligentBillAnalyzer()
        
        # Process multiple bills
        water_report = analyzer.process_multiple_bills(pdf_files)
        
        # Print detailed report
        logger.info("\n=== 6-Month Water Conservation Report ===")
        logger.info(f"Title: {water_report.get('title', 'N/A')}")
        logger.info(f"Period: {water_report.get('period', 'N/A')}")
        
        logger.info("\n--- Trend Analysis ---")
        trend_analysis = water_report.get('trend_analysis', {})
        for key, value in trend_analysis.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")
        
        logger.info("\n--- Recommendations ---")
        for recommendation in water_report.get('recommendations', []):
            logger.info(recommendation)
        
        logger.info("\n--- Actionable Insights ---")
        actionable_insights = water_report.get('actionable_insights', {})
        for key, value in actionable_insights.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")

    except Exception as e:
        logger.error(f"Unexpected error processing water bills: {e}", exc_info=True)

if __name__ == "__main__":
    test_water_bill_trends()
