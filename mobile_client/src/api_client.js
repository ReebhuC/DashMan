import * as FileSystem from 'expo-file-system';

let CAMERA_IP = 'http://localhost:8080';

export function setCameraIp(ip) {
  CAMERA_IP = ip;
}

export async function pollForIncidents() {
  try {
    const response = await fetch(`${CAMERA_IP}/locked_incidents`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const incidents = await response.json();
    return incidents || [];
  } catch (error) {
    console.error('Failed to poll dashcam:', error.message);
    return [];
  }
}

export async function downloadIncident(incidentName) {
  try {
    const downloadUrl = `${CAMERA_IP}/download/${incidentName}`;
    const localUri = `${FileSystem.documentDirectory}${incidentName}`;
    
    console.log(`Downloading ${downloadUrl} to ${localUri}...`);
    const { uri } = await FileSystem.downloadAsync(downloadUrl, localUri);
    return uri;
  } catch (error) {
    console.error('Failed to download incident:', error.message);
    return null;
  }
}

export async function deleteIncident(incidentName) {
  try {
    const response = await fetch(`${CAMERA_IP}/incidents/${incidentName}`, {
      method: 'DELETE'
    });
    return response.ok;
  } catch (error) {
    console.error('Failed to delete incident:', error.message);
    return false;
  }
}

export async function getLocalIncidents() {
  try {
    const files = await FileSystem.readDirectoryAsync(FileSystem.documentDirectory);
    return files.filter(f => f.endsWith('.mp4'));
  } catch (error) {
    console.error('Failed to read local files:', error.message);
    return [];
  }
}