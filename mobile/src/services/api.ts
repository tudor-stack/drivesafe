/**
 * src/services/api.ts
 * Varianta de Hackathon - Fără Firebase, direct IP-ul local.
 */
import axios from 'axios';

// =========================================================================
// !!! CRITIC: PUNE IP-UL TĂU DE WI-FI AICI !!!
// Nu folosi 192.168.56.1 (ăla e de la VirtualBox).
// Caută în ipconfig -> "Wireless LAN adapter Wi-Fi" -> IPv4 Address.
// =========================================================================
const BACKEND_IP = '10.168.122.94'; // <-- MODIFICĂ AICI!
const BASE_URL = `http://${BACKEND_IP}:8000`;

const api = axios.create({ baseURL: BASE_URL });

// Interceptor măsluit: adaugă un token fals ca să nu crăpăm dacă backend-ul cere unul
api.interceptors.request.use(async (config) => {
  config.headers.Authorization = `Bearer hackathon_demo_token`;
  return config;
});

// ── Interfețele rămân intacte ─────────────────────────────────────────────

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

// ── API Calls ─────────────────────────────────────────────────────────────

export const tripsApi = {
  /** Trimite datele cursei pentru procesare AI către Python */
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

  /** Funcții mockuite pentru a nu crăpa interfața dacă le apelezi din greșeală */
  getHistory: async (limit = 20, offset = 0): Promise<{ trips: TripSummary[]; total: number }> => {
    return { trips: [], total: 0 };
  },

  getTripDetail: async (tripId: string): Promise<any> => {
    return null;
  },
};

export const usersApi = {
  getMe: async () => {
    return { name: "User Demo Hackathon" };
  },
};