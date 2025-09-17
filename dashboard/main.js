# Example Electron main.js for desktop app
const { app, BrowserWindow } = require('electron')

function createWindow () {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true
    }
  })
  win.loadURL('https://www.infinityai.pro')
}

app.whenReady().then(createWindow)
