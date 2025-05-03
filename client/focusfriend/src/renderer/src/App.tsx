import React, { useState, useEffect } from 'react'
// import Versions from './components/Versions'
// import electronLogo from './assets/electron.svg'

// Reference GIFs from the public directory using absolute paths
const focusedAstronautGif = 'https://github.com/YoussefZayed/FocusFriend/blob/main/client/focusfriend/public/focused.gif?raw=true'
const unfocusedAstronautGif = 'https://github.com/YoussefZayed/FocusFriend/blob/main/client/focusfriend/public/not-focused.gif?raw=true'

// Mock API function (replace with actual API call later)
const fetchFocusStatus = async (): Promise<{ focused: boolean }> => {
  try {
    const response = await fetch('http://127.0.0.1:5000/is-focused');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data; // Assuming the API returns { focused: boolean }
  } catch (error) {
    console.error("Could not fetch focus status:", error);
    // Return a default or fallback value in case of an error
    // For now, let's default to focused to avoid breaking the UI logic completely
    return { focused: true }; 
  }
}

// Define window heights (should match main process)
const COLLAPSED_HEIGHT = 550
const EXPANDED_HEIGHT = 720

function App(): React.JSX.Element {
  const [focusState, setFocusState] = useState<'focused' | 'unfocused'>('focused')
  const [question, setQuestion] = useState<string>('')
  const [answer, setAnswer] = useState<string>('')
  const [isAsking, setIsAsking] = useState<boolean>(false)
  const [isAskSectionExpanded, setIsAskSectionExpanded] = useState<boolean>(false) // State for expansion

  useEffect(() => {
    // Function to check status and update state
    const checkStatus = async () => {
      try {
        const status = await fetchFocusStatus()
        setFocusState(status.focused ? 'focused' : 'unfocused')
      } catch (error) {
        console.error('Error fetching focus status:', error)
        setFocusState('focused')
      }
    }

    // Initial check
    checkStatus()

    // Set interval to check every 3 seconds
    const intervalId = setInterval(checkStatus, 3000)

    // Cleanup interval on component unmount
    return () => clearInterval(intervalId)
  }, [])

  // useEffect for resizing window based on ask section expansion
  useEffect(() => {
    const targetHeight = isAskSectionExpanded ? EXPANDED_HEIGHT : COLLAPSED_HEIGHT;
    window.customAPI.resizeWindow(targetHeight);
  }, [isAskSectionExpanded]);

  // Function to handle asking a question
  const handleAskQuestion = async () => {
    if (!question.trim()) return // Don't ask if empty
    setIsAsking(true)
    setAnswer('Thinking...') // Provide immediate feedback
    try {
      const response = await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question }),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ answer: `HTTP error! status: ${response.status}` }));
        throw new Error(errorData.answer || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAnswer(data.answer || 'No answer received.');
    } catch (error) {
      console.error("Could not fetch answer:", error);
      setAnswer(`Error: ${error instanceof Error ? error.message : 'Failed to get answer.'}`);
    }
    setIsAsking(false)
    // setQuestion(''); // Optionally clear question input after asking
  }

  // Function to toggle the ask section
  const toggleAskSection = () => {
    setIsAskSectionExpanded(!isAskSectionExpanded)
    // Optionally clear answer when collapsing
    if (isAskSectionExpanded) {
        setAnswer('');
    }
  }

  // Remove unused ipcHandle if not needed
  // const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')

  return (
    <div className="app-container">
      {/* Title Bar */}
      <div className="title-bar">
        <div className="title-text">Focus Friend</div>
     
      </div>

      {/* Display different content based on focus state */}
      {focusState === 'focused' ? (
        <div className="animation-placeholder focused">
          <img src={focusedAstronautGif} alt="Focused Astronaut" className="status-animation" />
          <div className="status-text-container">
            <h1 className="status-text focused-text">FOCUSED</h1>
          </div>
        </div>
      ) : (
        <div className="animation-placeholder unfocused">
          <img src={unfocusedAstronautGif} alt="Unfocused Astronaut" className="status-animation" />
          <div className="status-text-container">
            <h1 className="status-text unfocused-text">NOT FOCUSED</h1>
          </div>
        </div>
      )}
      
      {/* To-Do List Section */}
      <div className="todo-section">
        <h2 className="todo-title">To-Do List</h2>
        <ul className="todo-list">
          <li className="todo-item">vibe code</li>
          <li className="todo-item">win hackathon</li>
        </ul>
      </div>

      {/* Ask Question Section - Now Collapsible */}
      <div className="ask-section">
        <h2 className="ask-title" onClick={toggleAskSection}>
          Ask About Your Focus {isAskSectionExpanded ? '▲' : '▼'} {/* Add indicator */}
        </h2>
        {isAskSectionExpanded && ( // Conditionally render content
          <>
            <textarea
              className="question-input"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., What was I working on yesterday afternoon?"
              rows={3}
              disabled={isAsking}
            />
            <button
              className="ask-button"
              onClick={handleAskQuestion}
              disabled={isAsking || !question.trim()}
            >
              {isAsking ? 'Asking...' : 'Ask AI'}
            </button>
            {answer && (
              <div className="answer-display">
                <p>{answer}</p>
              </div>
            )}
          </>
        )}
      </div>

      {/* End Day Button */}
      <div className="end-day-container">
        <button className="end-day-button" onClick={() => window.customAPI.closeApp()}>
          End Day
        </button>
      </div>

      {/* Remove other default elements if not needed */}
      {/*
      <img alt="logo" className="logo" src={electronLogo} />
      <div className="creator">Powered by electron-vite</div>
      <div className="text">
        Build an Electron app with <span className="react">React</span>
        &nbsp;and <span className="ts">TypeScript</span>
      </div>
      <p className="tip">
        Please try pressing <code>F12</code> to open the devTool
      </p>
      <div className="actions">
        <div className="action">
          <a href="https://electron-vite.org/" target="_blank" rel="noreferrer">
            Documentation
          </a>
        </div>
        <div className="action">
          <a target="_blank" rel="noreferrer" onClick={ipcHandle}>
            Send IPC
          </a>
        </div>
      </div>
      <Versions></Versions>
      */}
    </div>
  )
}

export default App
