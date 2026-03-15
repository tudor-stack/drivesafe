// mobile/src/services/firebaseConfig.js
import { initializeApp } from 'firebase/app';
import { initializeAuth, getReactNativePersistence } from 'firebase/auth';
import AsyncStorage from '@react-native-async-storage/async-storage';

const firebaseConfig = {
    apiKey: "LIPEȘTE_AICI",
    authDomain: "LIPEȘTE_AICI",
    projectId: "LIPEȘTE_AICI",
    storageBucket: "LIPEȘTE_AICI",
    messagingSenderId: "LIPEȘTE_AICI",
    appId: "LIPEȘTE_AICI"
};

// Inițializăm aplicația Firebase
const app = initializeApp(firebaseConfig);

// Inițializăm Autentificarea și o salvăm local ca să nu te delogheze la fiecare refresh
const auth = initializeAuth(app, {
    persistence: getReactNativePersistence(AsyncStorage)
});

export { auth };