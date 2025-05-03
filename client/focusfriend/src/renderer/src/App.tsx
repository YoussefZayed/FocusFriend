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

function App(): React.JSX.Element {
  const [focusState, setFocusState] = useState<'focused' | 'unfocused'>('focused')

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
