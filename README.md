# Sketch2Story
Transform children's sketches into educational stories with AI. This application allows users to upload a sketch, add keywords about what they want to teach, and get a personalized story. The web application generates a personalized story, and users can also play the story with their selected voice. The application also includes a vocabulary section that extracts several vocabulary words from the story to enhance learning.

### Key Benefits
Educational Focus: Adaptive vocabulary learning for different age groups
Multimodal Learning: Visual, auditory, and textual learning combined
AI-Powered: Advanced image captioning and story generation
Child-Friendly: Age-appropriate content with safety measures


### Features
#### Core Funtionality
- Image Analysis: Upload sketches and get images description with Microsoft GIT
- Story Generation: Create educational stories with GPT-4 based on the themes user input and use words align with the levels users choose
- Audio Generation: Generate naration of the story with OpenAI's TTS API
- Vocabulary Learning: Extract vocabulary for learning purposes
- Multi-Level Support: Beginner, Intermediate, and Advanced vocabulary levels

#### Technical Features
- RESTful API: Flask-based backend with comprehensive endpoints
- React Frontend: Modern, responsive user interface
- Error Handling: Robust error management and fallback systems
- Performance Optimization: Efficient model loading and caching

### Architecture
```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  React Frontend │    │  Flask Backend  │    │  AI Services    │
│                 │    │                 │    │                 │
│ • Image Upload  │───>│ • Image Process │───>│ • Hugging Face  │
│ • Story Display │    │ • Story Generate│    │ • OpenAI GPT-4  │
│ • Audio Player  │<───│ • Audio Create  │<───│ • OpenAI TTS    │
│ • Vocab Learning│    │ • API Endpoints │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Tech Stack
#### Frontend
- **React**:Interactive user interface
- **CSS3**
- **JavaScript**
#### Backend
- **Flask**: Python web framework
- **OpenAI GPT-4**: Story generation
- **OpenAI TTS API**: Audio generation
- **HuugingFace Transformers**: Image captioning(Microsoft GIT)

### Quick Start
### 1. Clone the Repository
```bash
git clone https://github.com/KelllyChen/Sketch2Story.git
cd Sketch2Story
```

### 2. Environment Variables
Create a `.env` file in the backend directory
```.env
HUGGINGFACE_HUB_TOKEN=""
OPENAI_API_KEY=""
```

### 3. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
```bash
pytohn app.py
```

### 4. Frontend Setup(Create another new terminal)
```bash
cd sketch2story-frontend
npm install
npm start
```
### Demo
1. Upload: Upload a sketch or drawing
2. Analyze: GIT describes what's in your image
3. Theme: Add keywords like "teaching children how to repect"
4. Generate: Get a personalized story with GPT-4
5. Play: Play the story with selected voice
6. Learn: Get several vocabulary words from the story with their definitions and example sentences 

### Testing

Run tests:

```bash
python -m unittest discover test -v 
```

Check test coverage:

```bash
coverage run -m pytest
coverage report -m
```
### Test Coverage

| Component | Coverage | 
|-----------|----------|
| Backend (app.py) | 72% | 
| Tests (test_app.py) | 99% | 
| **Total Coverage** | **86%** | 

*Coverage target: >80% ✓*

### Check Complexity and Security
```bash
radon cc app.py -s
bandit app.py
```

### Security & Privacy
#### Data Protection
- No Data Storage: Images and stories are not permanently stored
- Temporary Files: Audio files are automatically cleaned up
- Memory-Only Processing: All data processing happens in memory
- No User Tracking: No personal information is collected or stored

#### API Security

- Environment Variables: Sensitive keys stored securely
- Input Validation: File type and size validation
- Error Handling: No sensitive information in error messages
- CORS Configuration: Controlled cross-origin access

#### Content Safety

- Child-Friendly Content: AI prompts designed for educational, age-appropriate content
- Content Filtering: Vocabulary extraction focuses on educational words
- Positive Messaging: Stories emphasize positive values and morals

#### Responsible AI Practices

- Transparent Processing: Clear indication of AI-generated content
- Fallback Systems: Graceful handling of AI service failures
- Educational Focus: Content designed to support learning objectives
- Age-Appropriate: Vocabulary and content adapted to specified age groups

### Deployment Guide
Due the consideration of cost this project was not deployed on cloud so far

### License
This project is licensed under the MIT License






