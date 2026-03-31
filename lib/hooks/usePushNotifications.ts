"use client";

import { useEffect, useState } from "react";
import { getMessaging, onMessage } from "firebase/messaging";
import { initializeFirebase } from "@/lib/firebase";
import { notificationService } from "@/lib/notification-service";

export function usePushNotifications() {
  const [fcmToken, setFcmToken] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize Firebase and request notification permission
  useEffect(() => {
    if (typeof window === "undefined") return;

    const checkNotificationSupport = async () => {
      try {
        // Check if notifications are supported
        if (!("Notification" in window) || !("serviceWorker" in navigator)) {
          console.warn("Notifications not supported on this device");
          setIsSupported(false);
          return;
        }

        setIsSupported(true);

        // Check if already subscribed
        if (Notification.permission === "granted") {
          setIsSubscribed(true);
          await initializeFirebaseMessaging();
        } else if (Notification.permission !== "denied") {
          // Request permission
          const permission = await Notification.requestPermission();
          if (permission === "granted") {
            setIsSubscribed(true);
            await initializeFirebaseMessaging();
          }
        }
      } catch (err) {
        console.error("Notification check error:", err);
        setError(
          err instanceof Error ? err.message : "Failed to setup notifications"
        );
      }
    };

    const initializeFirebaseMessaging = async () => {
      try {
        initializeFirebase();
        const messaging = getMessaging();

        // Get FCM token
        const token = await messaging.getToken({
          vapidKey: process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY,
        });

        if (token) {
          setFcmToken(token);
          // Register token with backend
          await notificationService.registerFCMToken(token);
        }

        // Listen for foreground messages
        onMessage(messaging, (payload) => {
          console.log("Message received in foreground:", payload);
          // Handle notification in foreground
          if (payload.notification) {
            new Notification(payload.notification.title || "LifeEcho", {
              body: payload.notification.body,
              icon: "/icons/icon-192x192.png",
            });
          }
        });
      } catch (err) {
        console.error("Firebase messaging setup error:", err);
        setError(
          err instanceof Error ? err.message : "Failed to setup Firebase messaging"
        );
      }
    };

    checkNotificationSupport();
  }, []);

  const unsubscribe = async () => {
    try {
      if (fcmToken) {
        await notificationService.unsubscribeFromNotifications(fcmToken);
        setFcmToken(null);
        setIsSubscribed(false);
      }
    } catch (err) {
      console.error("Unsubscribe error:", err);
      setError(
        err instanceof Error ? err.message : "Failed to unsubscribe from notifications"
      );
    }
  };

  return {
    fcmToken,
    isSupported,
    isSubscribed,
    error,
    unsubscribe,
  };
}
