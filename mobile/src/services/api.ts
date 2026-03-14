/**
 * src/services/api.ts
 * Singurul fișier din Mobile care știe URL-ul Backend-ului.
 * Persoana 3 implementează toate apelurile API aici.
 */
import axios from 'axios';
import auth from '@react-native-firebase/auth';

const BASE_URL = __DEV__
  ? 'http://localhost:8000'                              // dev local
  : 'https://drivesafe-backend-xxxx-ew.a.run.app';      // TODO: înlocuiește cu URL-ul real Cloud Run

const api = axios.create({ baseURL: BASE_URL });

// Interceptor: adaugă automat Firebase JWT la fiecare request
api.interceptors.request.use(async (config) => {
  const user = auth().currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Trips ─────────────────────────────────────────────────────────────────

export interface SensorWindow {
  timestamp: string;
  lat: number;
  lng: number;
  accel_magnitude_max: number;
  speed_change_rate: number;
  lateral_g: number;
  gyro_z_mean: number;
  speed_ms: number;
  heading_change_deg: number;
}

export interface GpsPoint {
  lat: number;
  lng: number;
  ts: string;
  speed_ms: number;
}

export interface TripEvent {
  event_id: string;
  behavior_type: string;
  timestamp: string;
  lat: number;
  lng: number;
  risk_score: number;
  severity_color: 'green' | 'yellow' | 'red';
  context: {
    road_type: string;
    speed_limit_kmh: number;
    speed_actual_kmh: number;
  };
}

export interface TripSummary {
  trip_id: string;
  start_time: string;
  end_time: string;
  distance_km: number;
  duration_minutes: number;
  global_score: number;
  events_count: number;
  status: 'processing' | 'done' | 'failed';
}

export interface TripDetail extends TripSummary {
  start_address: string;
  end_address: string;
  gps_polyline: GpsPoint[];
  events: TripEvent[];
  coach_report: string;
}

export const tripsApi = {
  /** Trimite datele cursei pentru procesare AI */
  processTrip: async (data: {
    trip_id: string;
    start_time: string;
    end_time: string;
    distance_km: number;
    sensor_windows: SensorWindow[];
    gps_polyline: GpsPoint[];
  }) => {
    const res = await api.post('/api/trips/process', data);
    return res.data;
  },

  /** Obține istoricul curselor */
  getHistory: async (limit = 20, offset = 0): Promise<{ trips: TripSummary[]; total: number }> => {
    const res = await api.get('/api/trips/history', { params: { limit, offset } });
    return res.data;
  },

  /** Obține detaliile complete ale unei curse */
  getTripDetail: async (tripId: string): Promise<TripDetail> => {
    const res = await api.get(`/api/trips/${tripId}`);
    return res.data;
  },
};

// ── Users ──────────────────────────────────────────────────────────────────

export const usersApi = {
  getMe: async () => {
    const res = await api.get('/api/users/me');
    return res.data;
  },
};
