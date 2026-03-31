"use client";

import { useState, useEffect } from "react";
import { Bell, BellOff } from "lucide-react";
import { usePushNotifications, useNotificationPreferences } from "@/lib/hooks";

export function NotificationSettings() {
  const { isSupported, isSubscribed, fcmToken, unsubscribe } =
    usePushNotifications();
  const { preferences, isLoading, updatePreferences } =
    useNotificationPreferences();
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState("");

  const handleToggleDailyDigest = async () => {
    if (!preferences) return;

    try {
      setIsSaving(true);
      await updatePreferences({
        enable_daily_digest: !preferences.enable_daily_digest,
      });
      setMessage("Daily digest preference updated!");
      setTimeout(() => setMessage(""), 3000);
    } catch (error) {
      setMessage("Failed to update preference");
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleTopStory = async () => {
    if (!preferences) return;

    try {
      setIsSaving(true);
      await updatePreferences({
        enable_top_story: !preferences.enable_top_story,
      });
      setMessage("Top story preference updated!");
      setTimeout(() => setMessage(""), 3000);
    } catch (error) {
      setMessage("Failed to update preference");
    } finally {
      setIsSaving(false);
    }
  };

  const handleUnsubscribe = async () => {
    if (confirm("Are you sure you want to disable all notifications?")) {
      try {
        await unsubscribe();
        setMessage("Notifications disabled");
        setTimeout(() => setMessage(""), 3000);
      } catch (error) {
        setMessage("Failed to disable notifications");
      }
    }
  };

  if (!isSupported) {
    return (
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <p className="text-sm text-gray-600">
          Notifications are not supported on your device
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <p className="text-sm text-gray-600">Loading notification settings...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {message && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          {message}
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Push Notifications</h3>
          {isSubscribed ? (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              <Bell size={14} />
              Enabled
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
              <BellOff size={14} />
              Disabled
            </span>
          )}
        </div>

        {isSubscribed && preferences ? (
          <div className="space-y-3 pt-4 border-t border-gray-200">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.enable_daily_digest}
                onChange={handleToggleDailyDigest}
                disabled={isSaving}
                className="w-4 h-4 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Daily story digest
              </span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.enable_top_story}
                onChange={handleToggleTopStory}
                disabled={isSaving}
                className="w-4 h-4 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Top story of the day
              </span>
            </label>

            <button
              onClick={handleUnsubscribe}
              disabled={isSaving}
              className="mt-4 text-sm text-red-600 hover:text-red-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Disable all notifications
            </button>
          </div>
        ) : (
          <p className="text-sm text-gray-600 pt-2">
            Enable notifications to receive daily digests and top story alerts
          </p>
        )}

        {fcmToken && (
          <p className="text-xs text-gray-500 pt-2 border-t border-gray-200 mt-4">
            Subscribed (Token: {fcmToken.substring(0, 20)}...)
          </p>
        )}
      </div>
    </div>
  );
}
