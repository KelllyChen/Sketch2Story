from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
import tempfile
import re
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global variables for model (load once)
image_model = None
image_processor = None

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Vocabulary difficulty levels
VOCABULARY_LEVELS = {
    "beginner": {
        "name": "Beginner (Ages 4-6)",
        "description": "Simple, everyday words",
        "target_length": "1-2 syllables",
        "examples": "happy, big, run, friend"
    },
    "intermediate": {
        "name": "Intermediate (Ages 7-9)", 
        "description": "Common academic words",
        "target_length": "2-3 syllables",
        "examples": "adventure, curious, important, explore"
    },
    "advanced": {
        "name": "Advanced (Ages 10-12)",
        "description": "Complex vocabulary and concepts",
        "target_length": "3+ syllables",
        "examples": "magnificent, courageous, responsibility, perseverance"
    }
}


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

def generate_story(image_description, keywords, story_length="short", vocabulary_level="intermediate"):
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
        
        # Get vocabulary level info
        vocab_info = VOCABULARY_LEVELS.get(vocabulary_level, VOCABULARY_LEVELS["intermediate"])
    
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
Vocabulary Level: {vocab_info['name']} - {vocab_info['description']}

Requirements:
- Make it educational and age-appropriate for children (ages 5-10)
- Include a clear moral lesson about: {keywords}
- Use vocabulary appropriate for {vocab_info['name']} level
- Target word complexity: {vocab_info['target_length']}
- Make the characters from the image description the main characters
- Include dialogue to make it more engaging
- End with a positive message
- Incorporate some educational vocabulary words that children can learn

Please write a complete, engaging children's story now:
"""

        response = client.chat.completions.create(
            model="gpt-4",  # You can also try "gpt-3.5-turbo" if GPT-4 isn't available
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a creative children's story writer who specializes in educational stories that teach important life lessons. Write engaging, age-appropriate stories for {vocab_info['name']} that are both fun and educational, using vocabulary appropriate for that age group."
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

def extract_vocabulary_words(story_text, vocabulary_level="intermediate"):
    """Extract vocabulary words from the story and create learning content"""
    try:
        vocab_info = VOCABULARY_LEVELS.get(vocabulary_level, VOCABULARY_LEVELS["intermediate"])
        
        prompt = f"""
Analyze the following children's story and extract vocabulary words appropriate for {vocab_info['name']} level learning.

Story: {story_text}

Please identify 6-8 vocabulary words from the story that are:
1. Appropriate for {vocab_info['name']} ({vocab_info['description']})
2. Educational and useful for children to learn
3. Not too common (avoid words like "the", "and", "is")
4. Target complexity: {vocab_info['target_length']}

For each word, provide:
- The word
- A simple, child-friendly definition
- The sentence from the story where it appears
- A fun example sentence that a child would understand

Format your response as a JSON array like this:
[
  {{
    "word": "example",
    "definition": "child-friendly definition",
    "story_sentence": "sentence from the story",
    "example_sentence": "fun example for kids"
  }}
]
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an educational content creator specializing in vocabulary development for children at {vocab_info['name']} level. Extract vocabulary words that are educational, age-appropriate, and help expand children's language skills."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        vocab_response = response.choices[0].message.content.strip()
        print("Vocabulary words extracted successfully!")
        
        # Try to parse JSON response
        
        try:
            # Clean the response in case there's extra text
            json_start = vocab_response.find('[')
            json_end = vocab_response.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                json_str = vocab_response[json_start:json_end]
                vocabulary_words = json.loads(json_str)
                return vocabulary_words
            else:
                raise ValueError("No JSON array found in response")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing vocabulary JSON: {e}")
            # Fallback: create a simple vocabulary list
            return create_fallback_vocabulary(story_text, vocabulary_level)
            
    except Exception as e:
        print(f"Error extracting vocabulary: {str(e)}")
        return create_fallback_vocabulary(story_text, vocabulary_level)

def create_fallback_vocabulary(story_text, vocabulary_level):
    """Create a simple fallback vocabulary list if AI extraction fails"""
    vocab_info = VOCABULARY_LEVELS.get(vocabulary_level, VOCABULARY_LEVELS["intermediate"])
    
    # Simple word extraction based on length and common educational words
    words = re.findall(r'\b[a-zA-Z]{4,}\b', story_text)
    
    # Filter and create simple vocabulary
    common_words = {'that', 'with', 'have', 'this', 'will', 'your', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'}
    
    filtered_words = [word.lower() for word in words if word.lower() not in common_words and len(word) >= 5]
    unique_words = list(dict.fromkeys(filtered_words))[:6]  # Remove duplicates and limit to 6
    
    fallback_vocab = []
    for word in unique_words:
        fallback_vocab.append({
            "word": word.capitalize(),
            "definition": f"An important word from our story - look it up together!",
            "story_sentence": f"This word appears in our story.",
            "example_sentence": f"Can you use '{word}' in your own sentence?"
        })
    
    return fallback_vocab


def generate_audio_narration(story_text, voice="nova"):
    """Generate audio narration using OpenAI TTS"""
    try:
        print("Generating audio narration...")
        
        # Create speech using OpenAI TTS
        response = client.audio.speech.create(
            model="tts-1",  
            voice=voice,    
            input=story_text,
            speed=0.9       # Slightly slower for children
        )
        
        # Create a temporary file to store the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.write(response.content)
        temp_file.close()
        
        print("Audio generated successfully!")
        return temp_file.name
        
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    api_key = os.getenv('OPENAI_API_KEY')
    return jsonify({
        "status": "healthy", 
        "message": "Flask backend with audio narration is running!",
        "openai_configured": api_key is not None,
        "features": ["image_captioning", "story_generation", "audio_narration", "vocabulary_learning"]
    })


@app.route('/vocabulary-levels', methods=['GET'])
def get_vocabulary_levels():
    """Get available vocabulary difficulty levels"""
    return jsonify({
        "success": True,
        "levels": VOCABULARY_LEVELS,
        "default": "intermediate"
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
    """Generate a story with vocabulary learning and optionally create audio narration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        image_description = data.get('imageDescription', '')
        keywords = data.get('keywords', '')
        story_length = data.get('storyLength', 'short')
        vocabulary_level = data.get('vocabularyLevel', 'intermediate')
        generate_audio = data.get('generateAudio', False)
        voice = data.get('voice', 'nova')
        
        if not image_description:
            return jsonify({"error": "Image description is required"}), 400
        
        if not keywords:
            return jsonify({"error": "Keywords are required"}), 400
        
        # Generate the story with vocabulary level consideration
        story = generate_story(image_description, keywords, story_length, vocabulary_level)
        
        if story.startswith("Error:"):
            return jsonify({"error": story}), 500
        
        # Extract vocabulary words from the story
        vocabulary_words = extract_vocabulary_words(story, vocabulary_level)
        
        response_data = {
            "success": True,
            "story": story,
            "imageDescription": image_description,
            "keywords": keywords,
            "vocabularyLevel": vocabulary_level,
            "vocabularyWords": vocabulary_words,
            "model": "GPT-4"
        }
        
        # Generate audio if requested
        if generate_audio:
            audio_file_path = generate_audio_narration(story, voice)
            if audio_file_path:
                # Convert audio to base64 for embedding in response
                with open(audio_file_path, 'rb') as audio_file:
                    audio_content = audio_file.read()
                    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                
                response_data.update({
                    "audioGenerated": True,
                    "audioData": f"data:audio/mp3;base64,{audio_base64}",
                    "voice": voice
                })
                
                # Clean up temp file
                os.unlink(audio_file_path)
            else:
                response_data.update({
                    "audioGenerated": False,
                    "audioError": "Failed to generate audio"
                })
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error generating story: {str(e)}")
        return jsonify({"error": f"Failed to generate story: {str(e)}"}), 500
    

@app.route('/voices', methods=['GET'])
def get_available_voices():
    """Get list of available TTS voices"""
    voices = [
        {"id": "alloy", "name": "Alloy", "description": "Neutral, balanced voice"},
        {"id": "echo", "name": "Echo", "description": "Clear, crisp voice"},
        {"id": "fable", "name": "Fable", "description": "Warm, storytelling voice"},
        {"id": "onyx", "name": "Onyx", "description": "Deep, rich voice"},
        {"id": "nova", "name": "Nova", "description": "Bright, cheerful voice (great for kids)"},
        {"id": "shimmer", "name": "Shimmer", "description": "Gentle, soothing voice"}
    ]
    
    return jsonify({
        "success": True,
        "voices": voices,
        "recommended": "nova"  # Best for children's stories
    })

if __name__ == '__main__':
    try:
        load_image_model()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("WARNING: OPENAI_API_KEY not found!")
        else:
            print("OpenAI API key found!")
            print("Audio narration enabled!")

        # Railway provides PORT environment variable
        port = int(os.environ.get('PORT', 5000))
        print(f"🚀 Starting Flask server on port {port}...")
        
        # Important: Set host to 0.0.0.0 for Railway
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()