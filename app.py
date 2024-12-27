from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from openai import AzureOpenAI

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Azure OpenAI endpoint and API key
azure_openai_endpoint = os.getenv("ENDPOINT_URL", "https://tscar.openai.azure.com/")
deployment_name = "DOG"  # Use a valid model name
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "e040ad84eb11423a93df36c7d9170d84")

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    azure_endpoint=azure_openai_endpoint,
    api_key=subscription_key,
    api_version="2024-05-13",
)

def get_product_info(product_name, date, file_content=None):
    prompt = f"estimate the day/month/year for when {product_name} will be 'Best by:', use exactly that format (ex: 'Best by: 10/20/2005'), assume {product_name} is refrigerated and bought on {date}; create a top 5 list of possible recipes using these ingredients, no description just names."
    if file_content:
        prompt += f" The file content is: {file_content.decode('utf-8')}"
    
    try:
        response = client.completions.create(
            model=deployment_name,
            prompt=prompt,
            max_tokens=200,
            temperature=0.0,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error fetching product info: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    # Extract the product_name and date from form data
    product_name = request.form.get('product_name')
    date = request.form.get('date')
    file = request.files.get('file')

    if not product_name or not date:
        return jsonify({"error": "Product name or date not provided"}), 400

    file_content = None
    if file:
        file_content = file.read()

    # Get product information from Azure OpenAI
    product_info = get_product_info(product_name, date, file_content)

    # Return the result as JSON
    return jsonify({"message": product_info})

if __name__ == '__main__':
    app.run(debug=True)
