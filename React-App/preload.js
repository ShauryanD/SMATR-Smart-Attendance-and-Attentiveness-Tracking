// const { contextBridge, ipcRenderer } = require('electron');

// contextBridge.exposeInMainWorld('api', {
//     fetchAttendance: (date) => ipcRenderer.invoke('fetch-attendance', date),
//     fetchAttentiveness: () => ipcRenderer.invoke('fetch-attentiveness')
// });

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  fetchAttendance: (date) => ipcRenderer.invoke('fetch-attendance', date),
  fetchAttentiveness: () => ipcRenderer.invoke('fetch-attentiveness')
});

