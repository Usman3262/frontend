"use client";

import { useEffect, useState } from "react";
import { Bell, X } from "lucide-react";
import { usePushNotifications } from "@/lib/hooks";

export function NotificationPrompt() {
  const { isSupported, isSubscribed } = usePushNotifications();
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    if (isSupported && !isSubscribed) {
      // Show prompt only once per session
      const hasShown = sessionStorage.getItem("notification-prompt-shown");
      if (!hasShown) {
        setShowPrompt(true);
        sessionStorage.setItem("notification-prompt-shown", "true");
      }
    }
  }, [isSupported, isSubscribed]);

  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm bg-white border border-gray-200 rounded-lg shadow-lg p-4 animate-in slide-in-from-bottom-5">
      <div className="flex items-start gap-3">
        <Bell size={20} className="text-blue-600 flex-shrink-0 mt-1" />
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">Stay Updated</h3>
          <p className="text-sm text-gray-600 mt-1">
            Get daily story digests and top story alerts in your browser
          </p>
          <p className="text-xs text-gray-500 mt-2">
            You can manage notification preferences anytime in settings
          </p>
        </div>
        <button
          onClick={() => setShowPrompt(false)}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600"
        >
          <X size={18} />
        </button>
      </div>
    </div>
  );
}
