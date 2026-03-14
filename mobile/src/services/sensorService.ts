/**
 * src/services/sensorService.ts
 * Citește accelerometru, giroscop și GPS și construiește SensorWindows.
 * Persoana 3 implementează acest serviciu.
 */
import { Accelerometer, Gyroscope } from 'expo-sensors';
import * as Location from 'expo-location';
import { SensorWindow, GpsPoint } from './api';

const SAMPLE_RATE_HZ = 50; // 50 samplings/secundă
const WINDOW_SIZE_MS = 2000; // fereastră de 2 secunde

interface RawSample {
  timestamp: number;
  ax: number; ay: number; az: number;
  gx: number; gy: number; gz: number;
  lat: number; lng: number;
  speed_ms: number;
  heading: number;
}

class SensorService {
  private samples: RawSample[] = [];
  private windows: SensorWindow[] = [];
  private gpsPolyline: GpsPoint[] = [];
  private isRecording = false;
  private accelSub: any = null;
  private gyroSub: any = null;
  private locationSub: any = null;

  // State curent GPS (actualizat independent de accel)
  private currentLat = 0;
  private currentLng = 0;
  private currentSpeed = 0;
  private currentHeading = 0;

  async startRecording() {
    this.isRecording = true;
    this.samples = [];
    this.windows = [];
    this.gpsPolyline = [];

    // Request permissions
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') throw new Error('Location permission denied');

    // GPS subscription
    this.locationSub = await Location.watchPositionAsync(
      { accuracy: Location.Accuracy.High, timeInterval: 1000, distanceInterval: 5 },
      (loc) => {
        this.currentLat = loc.coords.latitude;
        this.currentLng = loc.coords.longitude;
        this.currentSpeed = loc.coords.speed ?? 0;
        this.currentHeading = loc.coords.heading ?? 0;
        this.gpsPolyline.push({
          lat: loc.coords.latitude,
          lng: loc.coords.longitude,
          ts: new Date(loc.timestamp).toISOString(),
          speed_ms: loc.coords.speed ?? 0,
        });
      }
    );

    // Accelerometru la 50Hz
    Accelerometer.setUpdateInterval(1000 / SAMPLE_RATE_HZ);
    let gyroData = { x: 0, y: 0, z: 0 };

    this.gyroSub = Gyroscope.addListener((g) => { gyroData = g; });

    this.accelSub = Accelerometer.addListener((a) => {
      if (!this.isRecording) return;
      this.samples.push({
        timestamp: Date.now(),
        ax: a.x, ay: a.y, az: a.z,
        gx: gyroData.x, gy: gyroData.y, gz: gyroData.z,
        lat: this.currentLat,
        lng: this.currentLng,
        speed_ms: this.currentSpeed,
        heading: this.currentHeading,
      });
      this._processWindowIfReady();
    });
  }

  private _processWindowIfReady() {
    const now = Date.now();
    const windowStart = now - WINDOW_SIZE_MS;
    const windowSamples = this.samples.filter((s) => s.timestamp >= windowStart);

    if (windowSamples.length < 50) return; // minim 50 samples (1 secundă)

    // Curăță samplings vechi
    this.samples = this.samples.filter((s) => s.timestamp > windowStart - 500);

    // Calculează features din fereastră
    const accMags = windowSamples.map((s) =>
      Math.sqrt(s.ax * s.ax + s.ay * s.ay + s.az * s.az)
    );
    const speeds = windowSamples.map((s) => s.speed_ms);
    const headings = windowSamples.map((s) => s.heading);
    const gyroZ = windowSamples.map((s) => s.gz);

    const mean = (arr: number[]) => arr.reduce((a, b) => a + b, 0) / arr.length;

    const speedChangeRate =
      (speeds[speeds.length - 1] - speeds[0]) / (WINDOW_SIZE_MS / 1000);
    const headingChange = Math.abs(headings[headings.length - 1] - headings[0]);
    const lateralG = Math.max(...windowSamples.map((s) => Math.abs(s.ay)));

    const midSample = windowSamples[Math.floor(windowSamples.length / 2)];

    const window: SensorWindow = {
      timestamp: new Date().toISOString(),
      lat: midSample.lat,
      lng: midSample.lng,
      accel_magnitude_max: Math.max(...accMags),
      speed_change_rate: speedChangeRate,
      lateral_g: lateralG,
      gyro_z_mean: mean(gyroZ),
      speed_ms: mean(speeds),
      heading_change_deg: headingChange,
    };

    // Filtrează ferestre normale (nu le trimitem pe toate — doar cele interesante)
    const isDangerous =
      Math.abs(speedChangeRate) > 2.5 ||
      lateralG > 0.3 ||
      headingChange > 15;

    if (isDangerous) {
      this.windows.push(window);
    }
  }

  stopRecording() {
    this.isRecording = false;
    this.accelSub?.remove();
    this.gyroSub?.remove();
    this.locationSub?.remove();

    return {
      sensor_windows: this.windows,
      gps_polyline: this.gpsPolyline,
    };
  }
}

export const sensorService = new SensorService();
