import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { sensorService } from '../src/services/sensorService'; // Asigură-te că calea e corectă

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
            const data = sensorService.stopRecording();
            setIsTracking(false);
            setLastTripData(data);

            // Aici vezi dacă ai mișcat destul de tare telefonul!
            Alert.alert(
                "Cursă Oprită",
                `Am înregistrat ${data.sensor_windows.length} evenimente periculoase și ${data.gps_polyline.length} puncte GPS.`
            );
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