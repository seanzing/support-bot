import { useCallback, useState } from "react";
import { RotateCcw } from "lucide-react";

import { ChatKitPanel, THREAD_STORAGE_KEY } from "./ChatKitPanel";
import type { ColorScheme } from "../hooks/useColorScheme";

type EmbedViewProps = {
  scheme: ColorScheme;
  disclaimer?: boolean;
  disclaimerText?: string;
};

/**
 * Simplified embed view for the widget iframe.
 * Shows only the chat interface with branded header.
 * No stats, no panels, no extra UI - just clean chat.
 */
export function EmbedView({ scheme, disclaimer = false, disclaimerText = "" }: EmbedViewProps) {
  const [resetKey, setResetKey] = useState(0);

  const handleThreadChange = useCallback(() => {
    // No-op for embed view
  }, []);

  const handleResponseCompleted = useCallback(() => {
    // No-op for embed view
  }, []);

  const handleNewChat = useCallback(() => {
    // Clear stored thread from localStorage
    try {
      localStorage.removeItem(THREAD_STORAGE_KEY);
    } catch {
      // localStorage may be unavailable
    }
    // Increment resetKey to force ChatKitPanel remount with fresh state
    setResetKey((prev) => prev + 1);
  }, []);

  return (
    <div className="h-screen w-screen flex flex-col bg-background overflow-hidden">
      {/* Compact Header - Branding + New Chat */}
      <header className="flex-shrink-0 bg-[#6366F1] text-white px-3 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-white/20 flex items-center justify-center">
            <span className="font-bold text-sm">Z</span>
          </div>
          <div>
            <p className="font-semibold text-sm leading-tight">ZING Support</p>
            <p className="text-[10px] text-white/70">AI Assistant</p>
          </div>
        </div>
        <button
          onClick={handleNewChat}
          className="p-1.5 rounded-md bg-white/10 hover:bg-white/20 transition-colors"
          title="Start New Chat"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </header>

      {/* Chat Panel - Full Height */}
      <div className="flex-1 overflow-hidden">
        <ChatKitPanel
          key={resetKey}
          theme={scheme}
          onThreadChange={handleThreadChange}
          onResponseCompleted={handleResponseCompleted}
          disclaimer={disclaimer}
          disclaimerText={disclaimerText}
          resetKey={resetKey}
        />
      </div>
    </div>
  );
}
