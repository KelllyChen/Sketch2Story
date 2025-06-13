import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [caption, setCaption] = useState('');
  const [keywords, setKeywords] = useState('');
  const [storyLength, setStoryLength] = useState('short');
  const [story, setStory] = useState('');
  const [isProcessingImage, setIsProcessingImage] = useState(false);
  const [isGeneratingStory, setIsGeneratingStory] = useState(false);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState(1); // 1: Upload, 2: Keywords, 3: Story

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      setError('');
      setSelectedFile(file);
      setCaption('');
      setStory('');
      setCurrentStep(1);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const processImage = async () => {
    if (!selectedFile) return;

    setIsProcessingImage(true);
    setError('');

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch('http://localhost:5000/process-image', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setCaption(data.caption);
        setCurrentStep(2); // Move to keywords step
      } else {
        setError(data.error || 'Failed to process image');
      }
    } catch (err) {
      setError('Network error. Make sure Flask backend is running on port 5000');
      console.error('Error:', err);
    } finally {
      setIsProcessingImage(false);
    }
  };

  const generateStory = async () => {
    if (!caption || !keywords.trim()) return;

    setIsGeneratingStory(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5000/generate-story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          imageDescription: caption,
          keywords: keywords.trim(),
          storyLength: storyLength
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setStory(data.story);
        setCurrentStep(3); // Move to story result step
      } else {
        setError(data.error || 'Failed to generate story');
      }
    } catch (err) {
      setError('Network error. Make sure Flask backend is running on port 5000');
      console.error('Error:', err);
    } finally {
      setIsGeneratingStory(false);
    }
  };

  const resetApp = () => {
    setSelectedFile(null);
    setPreview('');
    setCaption('');
    setKeywords('');
    setStory('');
    setError('');
    setCurrentStep(1);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sketch2Story</h1>
        <p>Transform your sketches into educational stories with AI</p>
      </header>

      <main className="main-content">
        <div className="upload-container">
          
          {/* Step 1: Image Upload */}
          {currentStep === 1 && (
            <>
              <h2>Step 1: Upload Your Sketch</h2>
              
              <div className="file-upload">
                <label htmlFor="file-input" className="file-upload-label">
                  <div className="upload-area">
                    <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p><strong>Click to upload</strong> or drag and drop</p>
                    <p className="file-types">PNG, JPG, JPEG (MAX. 10MB)</p>
                  </div>
                </label>
                <input
                  id="file-input"
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>

              {preview && (
                <div className="preview-section">
                  <img src={preview} alt="Preview" className="image-preview" />
                  <button onClick={resetApp} className="reset-button">
                    Choose different image
                  </button>
                </div>
              )}

              <button
                onClick={processImage}
                disabled={!selectedFile || isProcessingImage}
                className={`process-button ${(!selectedFile || isProcessingImage) ? 'disabled' : ''}`}
              >
                {isProcessingImage ? (
                  <>
                    <div className="spinner"></div>
                    Analyzing Image...
                  </>
                ) : (
                  'Analyze Image'
                )}
              </button>
            </>
          )}

          {/* Step 2: Keywords Input */}
          {currentStep === 2 && (
            <>
              <h2>Step 2: Add Your Story Theme</h2>
              
              {preview && (
                <div className="preview-section">
                  <img src={preview} alt="Preview" className="image-preview" />
                </div>
              )}

              <div className="caption-result">
                <h3>Image Description:</h3>
                <p>{caption}</p>
              </div>

              <div className="keywords-section">
                <label htmlFor="keywords" className="keywords-label">
                  <strong>Story Theme/Keywords:</strong>
                </label>
                <input
                  id="keywords"
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g., teaching children how to respect, friendship, courage, helping others..."
                  className="keywords-input"
                />
                <p className="keywords-help">
                  Enter themes or moral lessons you want the story to focus on
                </p>
              </div>

              <div className="story-length-section">
                <label className="story-length-label">
                  <strong>Story Length:</strong>
                </label>
                <select 
                  value={storyLength} 
                  onChange={(e) => setStoryLength(e.target.value)}
                  className="story-length-select"
                >
                  <option value="short">Short Story (1-2 paragraphs)</option>
                  <option value="long">Longer Story (3-4 paragraphs)</option>
                </select>
              </div>

              <div className="button-group">
                <button onClick={resetApp} className="secondary-button">
                  Start Over
                </button>
                <button
                  onClick={generateStory}
                  disabled={!keywords.trim() || isGeneratingStory}
                  className={`process-button ${(!keywords.trim() || isGeneratingStory) ? 'disabled' : ''}`}
                >
                  {isGeneratingStory ? (
                    <>
                      <div className="spinner"></div>
                      Creating Story...
                    </>
                  ) : (
                    'Generate Story'
                  )}
                </button>
              </div>
            </>
          )}

          {/* Step 3: Story Result */}
          {currentStep === 3 && (
            <>
              <h2>Your Story is Ready!</h2>
              
              {preview && (
                <div className="preview-section">
                  <img src={preview} alt="Preview" className="image-preview" />
                </div>
              )}

              <div className="story-result">
                <h3>Generated Story:</h3>
                <div className="story-text">
                  {story}
                </div>
                
                <div className="story-details">
                  <p><strong>Based on:</strong> {caption}</p>
                  <p><strong>Theme:</strong> {keywords}</p>
                </div>
              </div>

              <div className="button-group">
                <button onClick={resetApp} className="secondary-button">
                  Create New Story
                </button>
                <button 
                  onClick={() => setCurrentStep(2)} 
                  className="secondary-button"
                >
                  Try Different Keywords
                </button>
              </div>
            </>
          )}

          {/* Error Display */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </div>
      </main>

      <footer>
        <p>Built with React & Flask • AI-Powered Story Generation</p>
      </footer>
    </div>
  );
}

export default App;