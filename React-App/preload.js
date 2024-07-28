const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  fetchAttendance: (date) => ipcRenderer.invoke('fetch-attendance', date),
  fetchAttentiveness: (date) => ipcRenderer.invoke('fetch-attentiveness', date)
});
