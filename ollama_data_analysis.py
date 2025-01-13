import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import base64

class OllamaDataAnalyzer:
    def __init__(self, ollama_url='http://localhost:11434/api/chat'):
        """
        Initialize the Ollama Data Analyzer
        
        :param ollama_url: URL for Ollama API chat endpoint
        """
        self.ollama_url = ollama_url
    
    def analyze_data(self, data, analysis_prompt=None):
        """
        Analyze data using Ollama's language model
        
        :param data: Input data to analyze (can be text, list, dict)
        :param analysis_prompt: Custom prompt for data analysis
        :return: Analyzed insights from Ollama
        """
        # Default analysis prompt if not provided
        if analysis_prompt is None:
            analysis_prompt = f"""
            Perform a comprehensive data analysis on the following data:
            {data}
            
            Please provide:
            1. Key insights and patterns
            2. Statistical summary
            3. Potential trends or observations
            4. Recommendations based on the data
            """
        
        # Prepare payload for Ollama API
        payload = {
            "model": "llama3.2",
            "messages": [
                {"role": "system", "content": "You are a professional data analyst."},
                {"role": "user", "content": analysis_prompt}
            ],
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['message']['content']
        except requests.exceptions.RequestException as e:
            return f"Error analyzing data: {str(e)}"
    
    def visualize_data(self, data, chart_type='bar'):
        """
        Create a visualization based on input data
        
        :param data: Dictionary or list of data to visualize
        :param chart_type: Type of chart to create (bar, pie, line)
        :return: Path to saved visualization
        """
        plt.figure(figsize=(10, 6))
        plt.title('Data Visualization')
        
        if chart_type == 'bar':
            categories = list(data.keys()) if isinstance(data, dict) else range(len(data))
            values = list(data.values()) if isinstance(data, dict) else data
            plt.bar(categories, values)
            plt.xlabel('Categories')
            plt.ylabel('Values')
        
        elif chart_type == 'pie':
            categories = list(data.keys()) if isinstance(data, dict) else range(len(data))
            values = list(data.values()) if isinstance(data, dict) else data
            plt.pie(values, labels=categories, autopct='%1.1f%%')
        
        elif chart_type == 'line':
            plt.plot(data)
            plt.xlabel('Index')
            plt.ylabel('Value')
        
        plt.tight_layout()
        visualization_path = 'c:/Users/Jestboi/Desktop/test/static/images/data_visualization.png'
        plt.savefig(visualization_path)
        plt.close()
        
        return visualization_path
    
    def process_and_analyze(self, data, analysis_prompt=None, chart_type='bar'):
        """
        Comprehensive data processing and analysis
        
        :param data: Input data to process
        :param analysis_prompt: Custom analysis prompt
        :param chart_type: Type of chart to create
        :return: Dictionary with analysis results and visualization
        """
        # Textual analysis
        textual_analysis = self.analyze_data(data, analysis_prompt)
        
        # Data visualization
        visualization_path = self.visualize_data(data, chart_type)
        
        return {
            'textual_analysis': textual_analysis,
            'visualization_path': visualization_path
        }
    
    def generate_graph_from_prompt(self, prompt):
        """
        Generate a graph based on a user's text prompt using Ollama
        
        :param prompt: User's text description of the graph
        :return: Dictionary with graph generation results
        """
        # Prepare payload for Ollama API
        payload = {
            "model": "llama3.2",
            "messages": [
                {"role": "system", "content": """
                You are a Python data visualization expert. 
                ABSOLUTE REQUIREMENTS:
                1. ONLY respond with VALID, EXECUTABLE Python code
                2. Use ONLY matplotlib.pyplot and pandas
                3. NO additional text or explanations
                4. WRAP code in ```python ``` markdown block
                5. ENSURE code is EXACTLY like this example:
                ```python
                import matplotlib.pyplot as plt
                import pandas as pd

                # Exactly this DataFrame creation
                data = pd.DataFrame({
                    'Category': ['A', 'B', 'C'],
                    'Values': [10, 20, 15]
                })

                # Exactly this plotting method
                plt.figure(figsize=(10, 6))
                plt.bar(data['Category'], data['Values'])
                plt.title('Sample Graph')
                plt.xlabel('Categories')
                plt.ylabel('Values')
                plt.tight_layout()
                plt.show()
                ```
                """},
                {"role": "user", "content": f"Generate a graph for this description: {prompt}"}
            ],
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Store the raw Ollama output for debugging
            raw_ollama_output = result['message']['content']
            
            graph_code = result['message']['content']
            
            # Extract code from markdown code block
            import re
            code_match = re.search(r'```python\n(.*?)```', graph_code, re.DOTALL)
            if code_match:
                graph_code = code_match.group(1)
            
            # Prepare execution environment
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import pandas as pd
            import io
            import traceback
            
            # Safe default graph function
            def create_default_graph():
                plt.figure(figsize=(10, 6))
                default_data = pd.DataFrame({
                    'Category': ['A', 'B', 'C'],
                    'Values': [10, 15, 7]
                })
                plt.bar(default_data['Category'], default_data['Values'])
                plt.title('Fallback Graph')
                plt.xlabel('Categories')
                plt.ylabel('Values')
                plt.tight_layout()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                fallback_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close()
                return fallback_base64
            
            # Capture plot in a bytes buffer
            buf = io.BytesIO()
            
            try:
                # Validate code
                if not graph_code.strip():
                    raise ValueError("Empty graph code")
                
                # Create a safe namespace
                namespace = {
                    'plt': plt, 
                    'pd': pd, 
                    'np': np
                }
                
                # Execute the code
                exec(graph_code, namespace)
                
                # Save the plot
                plt.tight_layout()
                plt.savefig(buf, format='png')
                buf.seek(0)
                
                # Convert to base64
                graph_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                
                return {
                    "status": "success",
                    "graph_code": graph_code,
                    "graph_image": graph_base64,
                    "raw_ollama_output": raw_ollama_output  # Add raw output to the response
                }
            
            except Exception as e:
                print(f"Code Execution Error: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                print(f"Problematic Code:\n{graph_code}")
                
                # Create and return fallback graph
                fallback_base64 = create_default_graph()
                
                return {
                    "status": "error",
                    "message": f"Error generating graph: {str(e)}",
                    "graph_image": fallback_base64,
                    "raw_ollama_output": raw_ollama_output  # Add raw output to the response
                }
            finally:
                plt.close('all')
    
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"API Request Error: {str(e)}"
            }

# Example usage
if __name__ == '__main__':
    # Sample data for demonstration
    sample_data = {
        'Sales': 1500,
        'Marketing': 800,
        'R&D': 1200,
        'Operations': 600
    }
    
    analyzer = OllamaDataAnalyzer()
    results = analyzer.process_and_analyze(sample_data)
    
    print("Textual Analysis:")
    print(results['textual_analysis'])
    print(f"\nVisualization saved at: {results['visualization_path']}")

    graph_prompt = "A line graph showing the sales trend over the last 6 months."
    graph_results = analyzer.generate_graph_from_prompt(graph_prompt)
    print("\nGraph Generation Results:")
    print(graph_results)
