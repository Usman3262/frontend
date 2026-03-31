"use client";

import { useEffect, useState } from "react";
import { notificationService } from "@/lib/notification-service";

interface NotificationPreferences {
  enable_daily_digest: boolean;
  enable_top_story: boolean;
}

export function useNotificationPreferences() {
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch preferences on mount
  useEffect(() => {
    const fetchPreferences = async () => {
      try {
        setIsLoading(true);
        const data = await notificationService.getNotificationPreferences();
        setPreferences(data);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch preferences:", err);
        setError(
          err instanceof Error ? err.message : "Failed to fetch preferences"
        );
        // Set default preferences on error
        setPreferences({
          enable_daily_digest: false,
          enable_top_story: false,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchPreferences();
  }, []);

  const updatePreferences = async (
    newPreferences: Partial<NotificationPreferences>
  ) => {
    try {
      const updated = { ...preferences, ...newPreferences } as NotificationPreferences;
      await notificationService.updateNotificationPreferences(updated);
      setPreferences(updated);
      setError(null);
      return updated;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to update preferences";
      setError(message);
      throw err;
    }
  };

  return {
    preferences,
    isLoading,
    error,
    updatePreferences,
  };
}
