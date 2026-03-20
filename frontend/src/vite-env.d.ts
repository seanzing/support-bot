/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPPORT_API_BASE?: string;
  readonly VITE_SUPPORT_CHATKIT_API_URL?: string;
  readonly VITE_SUPPORT_CUSTOMER_URL?: string;
  readonly VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY?: string;
  readonly VITE_SUPPORT_GREETING?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

