import { initializeApp, FirebaseApp } from "firebase/app";
import { getMessaging, Messaging } from "firebase/messaging";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

let app: FirebaseApp | null = null;
let messaging: Messaging | null = null;

export const initializeFirebase = (): FirebaseApp => {
  if (app) return app;

  app = initializeApp(firebaseConfig);
  return app;
};

export const getFirebaseMessaging = (): Messaging => {
  if (!messaging) {
    const firebaseApp = initializeFirebase();
    if (typeof window !== "undefined" && "serviceWorker" in navigator) {
      messaging = getMessaging(firebaseApp);
    }
  }
  return messaging as Messaging;
};

export default firebaseConfig;
