import type { StartScreenPrompt } from "@openai/chatkit-react";

export const THEME_STORAGE_KEY = "customer-support-theme";

/**
 * Backend API base path.
 * Uses relative path - works with both Vite proxy (dev) and nginx (prod).
 */
const SUPPORT_API_BASE = "/support";

/**
 * ChatKit domain key for API authentication.
 * Register your production domain at:
 * https://platform.openai.com/settings/organization/security/domain-allowlist
 */
export const SUPPORT_CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const SUPPORT_CHATKIT_API_URL = `${SUPPORT_API_BASE}/chatkit`;
export const SUPPORT_CUSTOMER_URL = `${SUPPORT_API_BASE}/customer`;
export const SUPPORT_TICKET_URL = `${SUPPORT_API_BASE}/ticket`;
export const SUPPORT_UPLOAD_URL = `${SUPPORT_API_BASE}/upload`;

export const SUPPORT_GREETING =
  "Hi! 👋 Welcome to ZING.\nWe help thousands of small businesses get found online and grow fast.\n\nHow can we help you today?";

export const SUPPORT_STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Get More Customers",
    prompt: "I want to get more customers for my business",
    icon: "sparkle",
  },
  {
    label: "Account Support",
    prompt: "I need help with my ZING account",
    icon: "lightbulb",
  },
];
