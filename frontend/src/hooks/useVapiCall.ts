import { useCallback, useEffect, useRef, useState } from "react";
import Vapi from "@vapi-ai/web";

const VAPI_PUBLIC_KEY = "2eaecbd1-fc1b-4c44-a376-c4a20207dcf8";
const VAPI_ASSISTANT_ID = "21526736-3921-432c-9a98-6e1267dae1cf";

export type VapiCallStatus = "idle" | "connecting" | "active" | "ended";

export function useVapiCall() {
  const vapiRef = useRef<Vapi | null>(null);
  const [status, setStatus] = useState<VapiCallStatus>("idle");

  useEffect(() => {
    const vapi = new Vapi(VAPI_PUBLIC_KEY);

    vapi.on("call-start", () => setStatus("active"));
    vapi.on("call-end", () => setStatus("idle"));
    vapi.on("error", () => setStatus("idle"));

    vapiRef.current = vapi;

    return () => {
      vapi.stop();
      vapiRef.current = null;
    };
  }, []);

  const startCall = useCallback(() => {
    if (!vapiRef.current || status === "connecting" || status === "active") return;
    setStatus("connecting");
    vapiRef.current.start(VAPI_ASSISTANT_ID);
  }, [status]);

  const endCall = useCallback(() => {
    if (!vapiRef.current) return;
    vapiRef.current.stop();
    setStatus("idle");
  }, []);

  const toggleCall = useCallback(() => {
    if (status === "active" || status === "connecting") {
      endCall();
    } else {
      startCall();
    }
  }, [status, startCall, endCall]);

  return { status, startCall, endCall, toggleCall };
}