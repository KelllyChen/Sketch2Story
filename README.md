# Sketch2Story
Transform children's sketch into educational stories with AI. This application allows users upload a sketch, add keywords anout what you want to teach, and get a personalized story.
## Update 3
### Features
- Image Analysis: Upload sketches and get images description with Microsoft GIT
- Story Generation: Create educational stories with GPT-4 based on the themes user input and use words align with the levels users choose
- Generate Audio: Generate naration of the story with OpenAI's TTS API
- Extract Vocabulary: Extract vocabulary for the goal of learning 

### Demo
1. Upload: Upload a sketch or drawing
2. Analyze: GIT describes what's in your image
3. Theme: Add keywords like "teaching children how to repect"
4. Generate: Get a personalized story with GPT-4
5. Play: Play the story with selected voice
6. Learn: Get several vocabulary from the story with their definitions and example sentences 

### Tech Stack
#### Frontend
- **React**:Interactive user interface
- **CSS3**
- **JavaScript**
#### Backend
- **Flask**: Python web framework
- **GPT-4**: Story generation
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







