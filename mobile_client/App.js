import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';
import { Video, ResizeMode } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { pollForIncidents, downloadIncident, deleteIncident, getLocalIncidents } from './src/api_client';

export default function App() {
  const [localIncidents, setLocalIncidents] = useState([]);
  const [status, setStatus] = useState('Initializing...');
  const [playingVideo, setPlayingVideo] = useState(null);

  const fetchLocalIncidents = async () => {
    const files = await getLocalIncidents();
    setLocalIncidents(files);
  };

  useEffect(() => {
    fetchLocalIncidents();

    const interval = setInterval(async () => {
      setStatus('Polling dashcam...');
      const serverIncidents = await pollForIncidents();
      
      let newDownloads = false;

      for (const incident of serverIncidents) {
        setStatus(`Downloading ${incident}...`);
        const localUri = await downloadIncident(incident);
        if (localUri) {
          newDownloads = true;
          setStatus(`Clearing ${incident} from dashcam SD card...`);
          await deleteIncident(incident);
        }
      }

      if (newDownloads) {
        await fetchLocalIncidents();
        setStatus('Sync complete.');
      } else {
        setStatus('Monitoring (10s interval)');
      }
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.header}>DASHMAN OS v0.1.0</Text>
      <Text style={styles.status}>STATUS: {status}</Text>
      
      {playingVideo ? (
        <View style={styles.videoContainer}>
          <Text style={styles.playingText}>PLAYING: {playingVideo.name}</Text>
          <Video
            source={{ uri: playingVideo.uri }}
            style={styles.video}
            useNativeControls
            resizeMode={ResizeMode.CONTAIN}
            isLooping
            shouldPlay
          />
          <TouchableOpacity style={styles.closeButton} onPress={() => setPlayingVideo(null)}>
            <Text style={styles.closeButtonText}>[ STOP PLAYBACK ]</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.listContainer}>
          <Text style={styles.subHeader}>LOCAL STORAGE (/incidents)</Text>
          {localIncidents.length === 0 ? (
            <Text style={styles.emptyText}>No incidents stored locally.</Text>
          ) : (
            <FlatList
              data={localIncidents}
              keyExtractor={(item) => item}
              renderItem={({ item }) => (
                <TouchableOpacity 
                  style={styles.incidentRow}
                  onPress={() => setPlayingVideo({ name: item, uri: `${FileSystem.documentDirectory}${item}` })}
                >
                  <Text style={styles.incidentText}>► {item}</Text>
                  <Text style={styles.playHint}>[ PLAY ]</Text>
                </TouchableOpacity>
              )}
            />
          )}
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
    padding: 20,
    paddingTop: 50,
  },
  header: {
    color: '#00FF00',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    fontFamily: 'Courier',
    textTransform: 'uppercase',
  },
  status: {
    color: '#FFB000',
    marginBottom: 20,
    fontFamily: 'Courier',
    fontSize: 14,
  },
  listContainer: {
    flex: 1,
    borderTopWidth: 1,
    borderTopColor: '#333333',
    paddingTop: 20,
  },
  subHeader: {
    color: '#00FF00',
    fontSize: 16,
    marginBottom: 15,
    fontFamily: 'Courier',
  },
  emptyText: {
    color: '#666666',
    fontFamily: 'Courier',
    fontStyle: 'italic',
  },
  incidentRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#111111',
    padding: 15,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#00FF00',
  },
  incidentText: {
    color: '#FFFFFF',
    fontFamily: 'Courier',
    fontSize: 16,
  },
  playHint: {
    color: '#00FF00',
    fontFamily: 'Courier',
    fontSize: 12,
  },
  videoContainer: {
    flex: 1,
    borderTopWidth: 1,
    borderTopColor: '#333333',
    paddingTop: 20,
    alignItems: 'center',
  },
  playingText: {
    color: '#00FF00',
    fontFamily: 'Courier',
    marginBottom: 15,
    alignSelf: 'flex-start',
  },
  video: {
    width: '100%',
    aspectRatio: 16 / 9,
    backgroundColor: '#111111',
    borderWidth: 1,
    borderColor: '#333333',
  },
  closeButton: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#222222',
  },
  closeButtonText: {
    color: '#FF3333',
    fontFamily: 'Courier',
    fontWeight: 'bold',
  }
});
