import io
import base64
import matplotlib.pyplot as plt
import numpy as np
import openai
import json

# OpenAI API Key (replace with your actual key)
openai.api_key = 'your-openai-api-key'

def generate_graph_from_prompt(prompt):
    """
    Generate a graph based on the user's text prompt using AI and Matplotlib
    """
    try:
        # Use OpenAI to interpret the prompt and generate graph details
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data visualization expert. Analyze the user's prompt and provide details for creating a matplotlib graph."},
                {"role": "user", "content": f"Create a graph based on this description: {prompt}. Provide: graph type, x-axis label, y-axis label, data points, title."}
            ]
        )
        
        graph_details = response.choices[0].message.content
        
        # Parse graph details (you might need more robust parsing)
        graph_type = "line"  # Default to line graph
        if "bar" in graph_details.lower():
            graph_type = "bar"
        elif "pie" in graph_details.lower():
            graph_type = "pie"
        
        # Generate sample data based on the prompt
        plt.figure(figsize=(10, 6))
        plt.title(f"Graph: {prompt}")
        
        if graph_type == "line":
            x = np.linspace(0, 10, 50)
            y = np.sin(x)
            plt.plot(x, y)
            plt.xlabel("X-axis")
            plt.ylabel("Y-axis")
        
        elif graph_type == "bar":
            categories = ['A', 'B', 'C', 'D', 'E']
            values = [np.random.randint(1, 100) for _ in range(5)]
            plt.bar(categories, values)
            plt.xlabel("Categories")
            plt.ylabel("Values")
        
        elif graph_type == "pie":
            sizes = [30, 20, 25, 15, 10]
            labels = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
            plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save plot to a bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        # Encode the image to base64
        graph_image = base64.b64encode(image_png).decode('utf-8')
        plt.close()
        
        return {
            "response": graph_details,
            "graph_image": graph_image
        }
    
    except Exception as e:
        return {
            "response": f"Error generating graph: {str(e)}",
            "graph_image": None
        }

def analyze_data_for_graph(data):
    """
    Analyze input data and suggest appropriate graph type
    """
    # Implement data analysis logic here
    pass
