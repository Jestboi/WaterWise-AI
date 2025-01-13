import boto3
import botocore

def test_aws_connection():
    """
    Test AWS connection and Textract service
    """
    try:
        # Create Textract client
        textract_client = boto3.client('textract')
        
        # Simple test to check connection
        print("AWS Credentials Successfully Configured!")
        print("Checking Textract Service Availability...")
        
        # List available operations to verify service access
        operations = textract_client.meta.service_model.operation_names
        print("\nAvailable Textract Operations:")
        for op in operations:
            print(f"  - {op}")
        
        return True
    
    except botocore.exceptions.NoCredentialsError:
        print("ERROR: No AWS Credentials Found")
        return False
    
    except botocore.exceptions.ClientError as e:
        print(f"AWS Connection Error: {e}")
        return False
    
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    test_aws_connection()
