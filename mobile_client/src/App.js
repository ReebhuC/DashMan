import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, Button, StyleSheet } from 'react-native';
import { pollForIncidents, downloadIncident, deleteIncident } from './api_client';

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [status, setStatus] = useState('Disconnected');

  useEffect(() => {
    const interval = setInterval(async () => {
      setStatus('Polling camera...');
      const newIncidents = await pollForIncidents();
      setIncidents(newIncidents);
      setStatus(newIncidents.length > 0 ? 'Incidents Found' : 'Monitoring');
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleDownloadAndUpscale = async (url) => {
    setStatus(`Downloading ${url}...`);
    const localPath = await downloadIncident(url);
    
    setStatus(`Deleting ${url} from camera...`);
    const deleted = await deleteIncident(url);
    if (!deleted) {
      console.warn(`Failed to delete ${url} from camera.`);
    }

    setStatus(`Running ESPCN AI Upscale on ${localPath}...`);
    // Placeholder for TFLite inference integration using react-native-fast-tflite
    setTimeout(() => {
      setStatus('Upscale Complete! Ready to playback.');
    }, 2000);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>DASHMAN OS v0.1</Text>
      <Text style={styles.status}>STATUS: {status}</Text>
      
      <FlatList
        data={incidents}
        keyExtractor={(item) => item}
        renderItem={({ item }) => (
          <View style={styles.incidentRow}>
            <Text style={styles.incidentText}>{item}</Text>
            <Button 
              title="Enhance" 
              color="#00FF00"
              onPress={() => handleDownloadAndUpscale(item)} 
            />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    padding: 20,
    paddingTop: 50,
  },
  header: {
    color: '#00FF00',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    fontFamily: 'monospace',
  },
  status: {
    color: '#00FF00',
    marginBottom: 20,
    fontFamily: 'monospace',
  },
  incidentRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
    paddingBottom: 10,
  },
  incidentText: {
    color: '#FFF',
    fontFamily: 'monospace',
  }
});