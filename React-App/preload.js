const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  fetchAttendance: () => ipcRenderer.invoke('fetch-attendance')
});
