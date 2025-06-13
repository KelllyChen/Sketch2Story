from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoProcessor, AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM
from PIL import Image
import torch
import os
import io
import base64
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global variables for model (load once)
image_model = None
image_processor = None

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def load_image_model():
    """Load the model once when the app starts"""
    global image_model, image_processor
    
    token = os.getenv('HUGGINGFACE_HUB_TOKEN')
    if not token:
        raise ValueError("HUGGINGFACE_HUB_TOKEN not found in environment variables.")
    
    print("Loading image captioning model...")
    image_model = AutoModelForCausalLM.from_pretrained("microsoft/git-base", token=token)
    image_processor = AutoProcessor.from_pretrained("microsoft/git-base", token=token)
    print("Image model loaded successfully!")

    

def generate_image_caption(image):
    """Generate caption for the uploaded image"""
    # Generate caption
    inputs = image_processor(images=image, return_tensors="pt")
    generated_ids = image_model.generate(pixel_values=inputs["pixel_values"], max_length=50)
    caption = image_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return caption

def generate_story(image_description, keywords, story_length="short"):
    """Generate a story using GPT-4"""

    try:
        # Debug: Print API key status
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"API Key exists: {api_key is not None}")
        print(f"API Key starts with 'sk-': {api_key.startswith('sk-') if api_key else False}")
        
        if not api_key:
            return "Error: OpenAI API key not found in environment variables."
        
        if not api_key.startswith('sk-'):
            return "Error: OpenAI API key format is incorrect. It should start with 'sk-'."
    
        # Create a detailed prompt
        if story_length == "short":
            length_instruction = "Write a short children's story (2-3 paragraphs)"
            max_tokens = 400
        else:
            length_instruction = "Write a detailed children's story (4-5 paragraphs)"
            max_tokens = 800
        
        prompt = f"""
{length_instruction} based on the following:

Image Description: {image_description}
Story Theme/Keywords: {keywords}

Requirements:
- Make it educational and age-appropriate for children (ages 5-10)
- Include a clear moral lesson about: {keywords}
- Use simple, engaging language
- Make the characters from the image description the main characters
- Include dialogue to make it more engaging
- End with a positive message

Please write a complete, engaging children's story now:
"""

        response = client.chat.completions.create(
            model="gpt-4",  # You can also try "gpt-3.5-turbo" if GPT-4 isn't available
            messages=[
                {
                    "role": "system", 
                    "content": "You are a creative children's story writer who specializes in educational stories that teach important life lessons. Write engaging, age-appropriate stories that are both fun and educational."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9
        )
        
        story = response.choices[0].message.content.strip()
        print("Story generated successfully!")
        return story
        
    except Exception as e:
        print(f"Error with GPT-4: {str(e)}")
        # Fallback to a simple response if GPT-4 fails
        return f"I'd love to tell you a story about {keywords} featuring {image_description}, but I'm having trouble connecting to my storytelling service right now. Please try again!"


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    api_key = os.getenv('OPENAI_API_KEY')
    return jsonify({
        "status": "healthy", 
        "message": "Flask backend is running with new OpenAI client!",
        "openai_configured": api_key is not None,
        "openai_key_format": api_key.startswith('sk-') if api_key else False,
        "openai_client": "new (>=1.0.0)"
    })

@app.route('/process-image', methods=['POST'])
def process_image():
    """Process uploaded image and return caption"""
    try:
        # Check if image file is in request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            return jsonify({"error": "File must be an image"}), 400
        
        # Load and process image
        image = Image.open(file.stream).convert("RGB")

        # Generate caption
        caption = generate_image_caption(image)
        
        
        return jsonify({
            "success": True,
            "caption": caption
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500
    

@app.route('/generate-story', methods=['POST'])
def generate_story_endpoint():
    """Generate a story based on image caption and user keywords"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        image_description = data.get('imageDescription', '')
        keywords = data.get('keywords', '')
        story_length = data.get('storyLength', 'short')  # 'short' or 'long'
        
        if not image_description:
            return jsonify({"error": "Image description is required"}), 400
        
        if not keywords:
            return jsonify({"error": "Keywords are required"}), 400
        
        
        
        # Generate the story
        story = generate_story(image_description, keywords, story_length)
        
        return jsonify({
            "success": True,
            "story": story,
            "imageDescription": image_description,
            "keywords": keywords,
            "model":"GPT-4"
        })
        
    except Exception as e:
        print(f"Error generating story: {str(e)}")
        return jsonify({"error": f"Failed to generate story: {str(e)}"}), 500

if __name__ == '__main__':
    # Load model before starting server
    try:
        load_image_model()
        print("Starting Flask server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Failed to start server: {e}")