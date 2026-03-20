import { useCallback, useEffect, useRef, useState } from "react";

import { SUPPORT_CUSTOMER_URL } from "../lib/config";

export type SupportInteraction = {
  timestamp: string;
  action_type: string;
  description: string;
  metadata: Record<string, unknown>;
};

export type CustomerProfile = {
  session_id: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  customer_company: string;
  session_started: string;
  questions_asked: number;
  kb_articles_viewed: number;
  tickets_created: number;
  interactions: SupportInteraction[];
};

type CustomerResponse = {
  customer: CustomerProfile;
};

// Request timeout in milliseconds (30 seconds)
const REQUEST_TIMEOUT_MS = 30000;

export function useCustomerContext(threadId: string | null) {
  const [profile, setProfile] = useState<CustomerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Track abort controller for cleanup
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchProfile = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);

    try {
      const url = threadId
        ? `${SUPPORT_CUSTOMER_URL}?thread_id=${encodeURIComponent(threadId)}`
        : SUPPORT_CUSTOMER_URL;

      const response = await fetch(url, {
        headers: { Accept: "application/json" },
        signal,
      });

      // Check if request was aborted
      if (signal?.aborted) {
        return;
      }

      if (!response.ok) {
        const statusMessages: Record<number, string> = {
          404: "Customer session not found",
          500: "Server error - please try again",
          401: "Authentication required",
          403: "Access denied",
        };
        throw new Error(statusMessages[response.status] || `Request failed (${response.status})`);
      }

      // Validate Content-Type
      const contentType = response.headers.get("Content-Type");
      if (!contentType?.includes("application/json")) {
        throw new Error("Invalid response format from server");
      }

      const payload = (await response.json()) as CustomerResponse;

      // Validate response structure
      if (!payload || typeof payload !== "object" || !payload.customer) {
        throw new Error("Invalid response structure from server");
      }

      // Only update state if request wasn't aborted
      if (!signal?.aborted) {
        setProfile(payload.customer);
      }
    } catch (err) {
      // Don't set error state if request was aborted (cleanup scenario)
      if (err instanceof Error && err.name === "AbortError") {
        return;
      }

      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      setProfile(null);
    } finally {
      // Only update loading state if not aborted
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  }, [threadId]);

  // Manual refresh function (creates new abort controller)
  const refresh = useCallback(async () => {
    // Cancel any in-flight request
    abortControllerRef.current?.abort();

    const controller = new AbortController();
    abortControllerRef.current = controller;

    // Set timeout to abort long-running requests
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      await fetchProfile(controller.signal);
    } finally {
      clearTimeout(timeoutId);
    }
  }, [fetchProfile]);

  // Effect for initial load and threadId changes
  useEffect(() => {
    // Cancel any previous in-flight request
    abortControllerRef.current?.abort();

    const controller = new AbortController();
    abortControllerRef.current = controller;

    // Set timeout
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    fetchProfile(controller.signal).finally(() => {
      clearTimeout(timeoutId);
    });

    // Cleanup: abort request on unmount or threadId change
    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [fetchProfile]);

  return { profile, loading, error, refresh };
}
