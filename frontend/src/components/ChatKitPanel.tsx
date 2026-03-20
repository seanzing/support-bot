import { useState } from "react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import type { ColorScheme } from "../hooks/useColorScheme";
import {
  SUPPORT_CHATKIT_API_DOMAIN_KEY,
  SUPPORT_CHATKIT_API_URL,
  SUPPORT_GREETING,
  SUPPORT_STARTER_PROMPTS,
  SUPPORT_UPLOAD_URL,
} from "../lib/config";

// LocalStorage key for session persistence
const THREAD_STORAGE_KEY = "zing-support-thread";

// Export for reset functionality
export { THREAD_STORAGE_KEY };

type ChatKitPanelProps = {
  theme: ColorScheme;
  onThreadChange: (threadId: string | null) => void;
  onResponseCompleted: () => void;
  disclaimer?: boolean;
  disclaimerText?: string;
  /** Increment to force a fresh conversation (clears thread state) */
  resetKey?: number;
};

const DEFAULT_DISCLAIMER = "AI may make mistakes. Please verify important information.";

export function ChatKitPanel({
  theme,
  onThreadChange,
  onResponseCompleted,
  disclaimer = false,
  disclaimerText = "",
  resetKey = 0,
}: ChatKitPanelProps) {
  // Session persistence: Load saved thread ID from localStorage on mount
  // When resetKey changes (via key prop on parent), this component remounts fresh
  const [initialThreadId] = useState<string | null>(() => {
    // If resetKey > 0, we're starting fresh - don't load from storage
    if (resetKey > 0) {
      return null;
    }
    try {
      return localStorage.getItem(THREAD_STORAGE_KEY);
    } catch {
      // localStorage may be unavailable in some contexts (e.g., sandboxed iframes)
      return null;
    }
  });

  const chatkit = useChatKit({
    // Session persistence: Start with the previously saved thread (if any)
    initialThread: initialThreadId,
    api: {
      url: SUPPORT_CHATKIT_API_URL,
      domainKey: SUPPORT_CHATKIT_API_DOMAIN_KEY,
      // Direct upload strategy - files go to backend /support/upload endpoint
      uploadStrategy: {
        type: "direct",
        uploadUrl: SUPPORT_UPLOAD_URL,
      },
    },
    theme: {
      colorScheme: theme,
      color: {
        grayscale: {
          hue: 240,           // ZING uses zinc/slate hues
          tint: 6,
          shade: theme === "dark" ? -1 : -4,
        },
        accent: {
          // ZING Brand Purple/Indigo
          primary: theme === "dark" ? "#818CF8" : "#6366F1",  // indigo-400 / indigo-500
          level: 1,
        },
      },
      radius: "round",
      // Compact density for better mobile experience
      density: "compact",
      // Custom typography with Inter font for brand consistency
      typography: {
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      },
    },
    startScreen: {
      greeting: SUPPORT_GREETING,
      prompts: SUPPORT_STARTER_PROMPTS,
    },
    composer: {
      placeholder: "Ask a question about your ZING services",
      // Image attachments enabled (uploadStrategy configured in api)
      attachments: {
        enabled: true,
      },
    },
    // Response actions: retry enabled, feedback disabled (no backend handler)
    threadItemActions: {
      feedback: false,
      retry: true,  // Let users retry if response is unsatisfactory
    },
    // History panel: allow deleting old conversations
    history: {
      enabled: true,
      showDelete: true,
      showRename: false,  // Thread titles auto-generated
    },
    // Widget action handling for Button clicks
    widgets: {
      onAction: async (action) => {
        if (action.type === "open_url" && action.payload?.url) {
          // Open URL in new tab with security attributes
          window.open(action.payload.url, "_blank", "noopener,noreferrer");
        }
      },
    },
    // AI disclaimer - only include config when enabled (undefined = hidden)
    disclaimer: disclaimer
      ? { text: disclaimerText || DEFAULT_DISCLAIMER }
      : undefined,
    // Hide ChatKit's internal header - both Home and EmbedView have custom branded headers
    header: {
      enabled: false,
    },
    onResponseEnd: () => {
      onResponseCompleted();
    },
    onThreadChange: ({ threadId }) => {
      // Session persistence: Save thread ID to localStorage for continuity
      try {
        if (threadId) {
          localStorage.setItem(THREAD_STORAGE_KEY, threadId);
        }
      } catch {
        // localStorage may be unavailable in some contexts
      }
      onThreadChange(threadId ?? null);
    },
    onError: ({ error }) => {
      // ChatKit displays surfaced errors; we keep logging for debugging.
      console.error("ChatKit error", error);
    },
  });

  return <ChatKit control={chatkit.control} className="block h-full w-full" />;
}
