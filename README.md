# Sketch2Story
Transform children's sketch into educational stories with AI. This application allows users upload a sketch, add keywords anout what you want to teach, and get a personalized story.
## Week1
### Features
- Image Analysis: Upload sketches and get images description with Microsoft GIT
- Story Generation: Create educational stories with GPT-4 based on the themes user input
### Demo
1. Upload: Upload a sketch or drawing
2. Analyze: GIT describes what's in your image
3. Theme: Add keywords like "teaching children how to repect"
4. Generate: Get a personalized story with GPT-4

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
### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### 3. Environment Variables
Create a `.env` file in the backend directory
```.env
HUGGINGFACE_HUB_TOKEN=""
OPENAI_API_KEY=""
```

### 4. Frontend Setup
```bash
cd sketch2story-frontend
npm install
npm start
```

## Next few steps
- Improve UI
- Generates 4 illustrated panels for key moments
- Converts story into narrated audio
- Outputs an interactive storybook
- Let users save the story





