import os
import logging
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from utils.intelligent_bill_analyzer import IntelligentBillAnalyzer

def test_pdf_extraction():
    """
    Test PDF extraction from uploads directory
    """
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pdf_extraction_debug.log', mode='w'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('PDFExtractionTest')

    # Find uploads directory
    uploads_dir = os.path.join(project_dir, 'uploads')
    
    if not os.path.exists(uploads_dir):
        logger.error(f"Uploads directory does not exist: {uploads_dir}")
        return

    # List PDF files in uploads directory
    try:
        pdf_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {uploads_dir}")
            return

        logger.info(f"Found {len(pdf_files)} PDF files")
        
        # Initialize analyzer
        analyzer = IntelligentBillAnalyzer()
        
        # Analyze first PDF
        first_pdf = pdf_files[0]
        pdf_path = os.path.join(uploads_dir, first_pdf)
        
        logger.info(f"\n--- Analyzing PDF: {first_pdf} ---")
        
        # Extract text using different methods
        logger.info("1. Extracting text with PyPDF2")
        pdf_text = analyzer.extract_text_from_pdf(pdf_path)
        logger.info(f"PyPDF2 Extracted Text Length: {len(pdf_text)}")
        logger.info(f"First 500 characters:\n{pdf_text[:500]}")
        
        logger.info("\n2. Analyzing with Textract")
        textract_result = analyzer.analyze_document_with_textract(pdf_path)
        
        # Print detailed results
        logger.info("\nTextract Analysis Results:")
        logger.info(f"Success: {textract_result.get('success', False)}")
        logger.info(f"Extraction Method: {textract_result.get('extraction_method', 'Unknown')}")
        
        if textract_result.get('success', False):
            full_text = textract_result.get('full_text', '')
            logger.info(f"Extracted Text Length: {len(full_text)}")
            logger.info(f"First 500 characters:\n{full_text[:500]}")
        else:
            logger.error(f"Analysis failed: {textract_result.get('error', 'Unknown error')}")
        
        # Attempt to parse bill details
        logger.info("\n3. Parsing Bill Details")
        parsed_details = analyzer.parse_bill_details(full_text)
        logger.info("Parsed Details:")
        for key, value in parsed_details.items():
            logger.info(f"  {key}: {value}")
        
        # Generate bill insights
        logger.info("\n4. Generating Bill Insights")
        bill_insights = analyzer.generate_bill_insights(parsed_details)
        logger.info("Bill Insights:")
        for category, details in bill_insights.items():
            logger.info(f"\n{category.capitalize()}:")
            if isinstance(details, dict):
                for key, value in details.items():
                    logger.info(f"  {key.capitalize()}: {value}")
            else:
                logger.info(f"  {details}")

    except Exception as e:
        logger.error(f"Unexpected error processing PDFs: {e}", exc_info=True)

if __name__ == "__main__":
    test_pdf_extraction()
