import unittest
import json
import os
import io
import sys
from unittest.mock import patch, MagicMock
from PIL import Image

os.environ['OPENAI_API_KEY'] = 'sk-test-fake-key-for-testing'
os.environ['HUGGINGFACE_HUB_TOKEN'] = 'hf_test_fake_token_for_testing'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app import app, generate_image_caption, generate_story, generate_audio_narration,extract_vocabulary_words, create_fallback_vocabulary, VOCABULARY_LEVELS

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def create_test_image(self):
        """Create a test image file"""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return img_io
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('features', data)

    def test_vocabulary_levels_endpoint(self):
        """Test the vocabulary levels endpoint"""
        response = self.app.get('/vocabulary-levels')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('levels', data)
        self.assertEqual(data['default'], 'intermediate')
        self.assertIn('beginner', data['levels'])
        self.assertIn('intermediate', data['levels'])
        self.assertIn('advanced', data['levels'])

    def test_voice_endpoint(self):
        """Test the voices endpoint"""
        response = self.app.get('/voices')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['voices']), 6)
        self.assertEqual(data['recommended'], 'nova')

    @patch('backend.app.generate_image_caption')
    def test_process_image_success(self, mock_caption):
        mock_caption.return_value = "A red square"
        test_image = self.create_test_image()
        response = self.app.post('/process-image',
                                data={'image': (test_image, 'test.jpg')},
                                content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['caption'], 'A red square')

    def test_process_image_no_file(self):
        """Test image processing without file"""
        response = self.app.post('/process-image')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)


    @patch('backend.app.generate_story')
    def test_generate_story_success(self, mock_story):
        """Test successful story generation"""
        mock_story.return_value = "Once upon a time..."
        
        payload = {
            'imageDescription': 'A cat in a garden',
            'keywords': 'friendship, courage'
        }
        
        response = self.app.post('/generate-story',
                                data=json.dumps(payload),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('story', data)
    
    def test_generate_story_missing_data(self):
        """Test story generation with missing data"""
        payload = {'imageDescription': 'A dog'}  # Missing keywords
        
        response = self.app.post('/generate-story',
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        



class TestCoreFunctions(unittest.TestCase):
    """Test core application functions"""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('backend.app.client')
    def test_generate_story_with_api_key(self, mock_client):
        """Test story generation with valid API key"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "A wonderful story..."
        mock_client.chat.completions.create.return_value = mock_response
        
        result = generate_story("A rabbit", "kindness", "short")
        
        self.assertEqual(result, "A wonderful story...")
        mock_client.chat.completions.create.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_generate_story_no_api_key(self):
        """Test story generation without API key"""
        result = generate_story("A cat", "patience")
        self.assertIn("Error: OpenAI API key not found", result)
    
    def test_generate_story_invalid_api_key(self):
        """Test story generation with invalid API key"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}):
            result = generate_story("A dog", "loyalty")
            self.assertIn("Error: OpenAI API key format is incorrect", result)
    
    @patch('backend.app.image_model')
    @patch('backend.app.image_processor')
    def test_generate_image_caption(self, mock_processor, mock_model):
        """Test image caption generation"""
        # Mock the model behavior
        mock_processor.return_value = {"pixel_values": "test"}
        mock_model.generate.return_value = ["generated_ids"]
        mock_processor.batch_decode.return_value = ["a test image"]
        
        # Create test image
        test_image = Image.new('RGB', (100, 100), color='blue')
        
        result = generate_image_caption(test_image)
        self.assertEqual(result, "a test image")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('backend.app.client')
    @patch('tempfile.NamedTemporaryFile')
    def test_generate_audio_narration(self, mock_temp_file, mock_client):
        """Test audio generation"""
        # Mock OpenAI TTS response
        mock_response = MagicMock()
        mock_response.content = b"fake audio data"
        mock_client.audio.speech.create.return_value = mock_response
        
        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.mp3"
        mock_temp_file.return_value = mock_file
        
        result = generate_audio_narration("Test story", "nova")
        
        self.assertEqual(result, "/tmp/test.mp3")
        mock_client.audio.speech.create.assert_called_once()

    @patch('backend.app.client')
    def test_extract_vocabulary_words_success(self, mock_client):
        """Test vocabulary extraction success"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''[
            {
                "word": "adventure",
                "definition": "an exciting journey",
                "story_sentence": "The adventure began",
                "example_sentence": "Going camping is an adventure"
            }
        ]'''
        mock_client.chat.completions.create.return_value = mock_response
        
        result = extract_vocabulary_words("The adventure began with courage", "intermediate")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['word'], 'adventure')

    @patch('backend.app.client')
    def test_extract_vocabulary_words_invalid_json(self, mock_client):
        """Test vocabulary extraction with invalid JSON response"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Invalid JSON response"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = extract_vocabulary_words("A simple story", "beginner")
        
        # Should return fallback vocabulary
        self.assertIsInstance(result, list)

    @patch('backend.app.client')
    def test_extract_vocabulary_words_exception(self, mock_client):
        """Test vocabulary extraction when API throws exception"""
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = extract_vocabulary_words("A story with words", "advanced")
        
        # Should return fallback vocabulary
        self.assertIsInstance(result, list)

class TestVocabularyLevels(unittest.TestCase):
    """Test vocabulary level functionality"""
    
    def test_vocabulary_levels_constants(self):
        """Test vocabulary levels are properly defined"""
        self.assertIn('beginner', VOCABULARY_LEVELS)
        self.assertIn('intermediate', VOCABULARY_LEVELS)
        self.assertIn('advanced', VOCABULARY_LEVELS)
        
        # Test structure of each level
        for level_key, level_data in VOCABULARY_LEVELS.items():
            self.assertIn('name', level_data)
            self.assertIn('description', level_data)
            self.assertIn('target_length', level_data)
            self.assertIn('examples', level_data)

    @patch('backend.app.client')
    def test_story_generation_all_vocabulary_levels(self, mock_client):
        """Test story generation with all vocabulary levels"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "A story adapted to vocabulary level"
        mock_client.chat.completions.create.return_value = mock_response
        
        levels = ['beginner', 'intermediate', 'advanced']
        
        for level in levels:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-valid-key'}):
                result = generate_story("A cat", "friendship", "short", level)
                self.assertEqual(result, "A story adapted to vocabulary level")


class TestIntegration(unittest.TestCase):
    """Test end-to-end workflows"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('backend.app.generate_image_caption')
    @patch('backend.app.generate_story')
    def test_full_workflow(self, mock_story, mock_caption):
        """Test complete image -> story workflow"""
        # Mock responses
        mock_caption.return_value = "A happy dog in a park"
        mock_story.return_value = "Buddy the dog loved playing in the park..."
        
        # Step 1: Upload image
        img = Image.new('RGB', (100, 100), color='green')
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        
        image_response = self.app.post('/process-image',
                                     data={'image': (img_io, 'dog.jpg')},
                                     content_type='multipart/form-data')
        
        self.assertEqual(image_response.status_code, 200)
        image_data = json.loads(image_response.data)
        
        # Step 2: Generate story
        story_payload = {
            'imageDescription': image_data['caption'],
            'keywords': 'friendship, joy',
            'vocabularyLevel': 'intermediate',
            'storyLength': 'short'
        }
        
        story_response = self.app.post('/generate-story',
                                     data=json.dumps(story_payload),
                                     content_type='application/json')
        
        self.assertEqual(story_response.status_code, 200)
        story_data = json.loads(story_response.data)
        self.assertTrue(story_data['success'])
        self.assertIn('Buddy', story_data['story'])
        self.assertIn('vocabularyWords', story_data)
       



if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)



        

    


