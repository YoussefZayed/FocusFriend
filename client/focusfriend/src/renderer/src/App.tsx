import React, { useState, useEffect } from 'react'
// import Versions from './components/Versions'
// import electronLogo from './assets/electron.svg'

// Reference GIFs from the public directory using absolute paths
const focusedAstronautGif = '/focused.gif'
const unfocusedAstronautGif = '/not-focused.gif'

// Mock API function (replace with actual API call later)
let isFocused = true // Start with focused state
const fetchFocusStatus = async (): Promise<{ focused: boolean }> => {
  // Simulate API call delay
  await new Promise((resolve) => setTimeout(resolve, 100))
  // Toggle the status for demonstration
  isFocused = !isFocused
  console.log('Mock API: User focused =', isFocused)
  return { focused: isFocused }
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
      {/* Display different content based on focus state */}
      {focusState === 'focused' ? (
        <div className="animation-placeholder focused">
          <img src={focusedAstronautGif} alt="Focused Astronaut" className="status-animation" />
          <h1 className="status-text focused-text">FOCUSED</h1>
        </div>
      ) : (
        <div className="animation-placeholder unfocused">
          <img src={unfocusedAstronautGif} alt="Unfocused Astronaut" className="status-animation" />
          <h1 className="status-text unfocused-text">NOT FOCUSED</h1>
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
