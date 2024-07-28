const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  });

  win.loadFile('index.html');
}

ipcMain.handle('fetch-attentiveness', async (event, date) => {
  try {
    const response = await axios.get('http://127.0.0.1:5001/attentiveness', {
      params: {
        date: date
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching attentiveness data:', error);
    return { error: 'Failed to fetch attentiveness data' };
  }
});

ipcMain.handle('fetch-attendance', async (event, date) => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/attendance', {
      params: {
        date: date
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching attendance data:', error);
    return { error: 'Failed to fetch attendance data' };
  }
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

