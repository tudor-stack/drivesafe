import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { sensorService } from '../src/services/sensorService';
import { tripsApi } from '../src/services/api'; // IMPORT CRITIC LIPSĂ

export default function Dashboard() {
    const [isTracking, setIsTracking] = useState(false);
    const [lastTripData, setLastTripData] = useState<any>(null);

    const toggleTracking = async () => {
        if (!isTracking) {
            try {
                await sensorService.startRecording();
                setIsTracking(true);
                setLastTripData(null);
            } catch (error) {
                Alert.alert("Eroare", "Nu am putut porni senzorii. Ai dat permisiunea de locație?");
            }
        } else {
            // 1. Oprim senzorii și salvăm datele local
            const data = sensorService.stopRecording();
            setIsTracking(false);
            setLastTripData(data);

            // 2. PARTEA LIPSĂ: Trimitem datele la Backend-ul de Python
            try {
                const payload = {
                    trip_id: `trip_${Date.now()}`,
                    sensor_windows: data.sensor_windows,
                    gps_polyline: data.gps_polyline,
                    start_time: new Date().toISOString(),
                    end_time: new Date().toISOString(),
                    distance_km: 0.5 // Valoare de test
                };

                // Aici telefonul "strigă" laptopul folosind IP-ul din api.ts
                const response = await tripsApi.processTrip(payload);

                Alert.alert(
                    "Analiză AI Completă",
                    `Evenimente: ${data.sensor_windows.length}\nScor obținut: ${response.global_score ?? 'Fără scor'}`
                );
            } catch (err) {
                console.error(err);
                Alert.alert(
                    "Eroare de Conexiune",
                    "Senzorii au oprit cursa, dar laptopul nu a răspuns. Verifică IP-ul sau Firewall-ul!"
                );
            }
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>DriveSafe AI</Text>

            <View style={styles.card}>
                <Text style={styles.status}>
                    Status: {isTracking ? "🟢 Senzori Activi" : "🔴 Oprit"}
                </Text>
                {isTracking && <Text style={styles.warning}>Scutură telefonul pentru a genera date!</Text>}

                {!isTracking && lastTripData && (
                    <Text style={styles.results}>
                        Ultima cursă: {lastTripData.sensor_windows.length} alerte.
                    </Text>
                )}
            </View>

            <TouchableOpacity
                style={[styles.button, isTracking ? styles.buttonStop : styles.buttonStart]}
                onPress={toggleTracking}
            >
                <Text style={styles.buttonText}>
                    {isTracking ? "Oprește Cursa" : "Start Cursă"}
                </Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#121212' },
    title: { fontSize: 28, fontWeight: 'bold', marginBottom: 30, color: '#ffffff' },
    card: { padding: 20, backgroundColor: '#1e1e1e', borderRadius: 10, marginBottom: 30, width: '80%', alignItems: 'center', elevation: 3 },
    status: { fontSize: 18, fontWeight: 'bold', marginBottom: 10, color: '#ffffff' },
    warning: { color: '#ff9800', marginTop: 10, textAlign: 'center' },
    results: { color: '#4CAF50', marginTop: 10, fontWeight: 'bold' },
    button: { padding: 15, borderRadius: 10, width: '80%', alignItems: 'center' },
    buttonStart: { backgroundColor: '#4CAF50' },
    buttonStop: { backgroundColor: '#F44336' },
    buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold' }
});