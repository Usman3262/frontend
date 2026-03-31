const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const notificationService = {
  // Get FCM token (called from frontend)
  registerFCMToken: async (fcmToken: string) => {
    return fetch(`${API_BASE_URL}/notifications/register-token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fcm_token: fcmToken }),
    }).then((res) => res.json());
  },

  // Get top story of the day for digest
  getTopStoryDigest: async () => {
    return fetch(`${API_BASE_URL}/notifications/top-story-digest`).then((res) =>
      res.json()
    );
  },

  // Unsubscribe from notifications
  unsubscribeFromNotifications: async (fcmToken: string) => {
    return fetch(`${API_BASE_URL}/notifications/unsubscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fcm_token: fcmToken }),
    }).then((res) => res.json());
  },

  // Get notification preferences
  getNotificationPreferences: async () => {
    return fetch(`${API_BASE_URL}/notifications/preferences`).then((res) =>
      res.json()
    );
  },

  // Update notification preferences
  updateNotificationPreferences: async (preferences: {
    enable_daily_digest: boolean;
    enable_top_story: boolean;
  }) => {
    return fetch(`${API_BASE_URL}/notifications/preferences`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(preferences),
    }).then((res) => res.json());
  },
};
