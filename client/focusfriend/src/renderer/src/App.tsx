import React, { useState, useEffect } from 'react'
import Versions from './components/Versions'
import electronLogo from './assets/electron.svg'

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
  const [dogState, setDogState] = useState<'idle' | 'sad'>('idle')

  useEffect(() => {
    // Function to check status and update state
    const checkStatus = async () => {
      try {
        const status = await fetchFocusStatus()
        setDogState(status.focused ? 'idle' : 'sad')
      } catch (error) {
        console.error('Error fetching focus status:', error)
        // Optionally set a default or error state
        setDogState('idle') // Default to idle on error
      }
    }

    // Initial check
    checkStatus()

    // Set interval to check every 3 seconds
    const intervalId = setInterval(checkStatus, 3000)

    // Cleanup interval on component unmount
    return () => clearInterval(intervalId)
  }, []) // Empty dependency array ensures this runs only once on mount

  const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')

  return (
    <div className="app-container">
      {/* Display different content based on state */}
      {dogState === 'idle' ? (
        <div className="animation-placeholder idle">
          <h2>Idle Dog Animation</h2>
          {/* Replace with actual idle animation component/element */}
        </div>
      ) : (
        <div className="animation-placeholder sad">
          <h2>Sad Dog Animation</h2>
          {/* Replace with actual sad animation component/element */}
        </div>
      )}
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
    </div>
  )
}

export default App
