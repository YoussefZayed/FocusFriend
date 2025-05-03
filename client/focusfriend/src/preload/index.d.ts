import { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI
    api: unknown
    customAPI: {
      closeApp: () => void
      resizeWindow: (height: number) => void
    }
  }
}
