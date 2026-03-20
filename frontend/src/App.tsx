import { useCallback, useMemo } from "react";

import Home from "./components/Home";
import { WidgetDemo } from "./components/WidgetDemo";
import { EmbedView } from "./components/EmbedView";
import type { ColorScheme } from "./hooks/useColorScheme";
import { useColorScheme } from "./hooks/useColorScheme";

export default function App() {
  const { scheme, setScheme } = useColorScheme();

  // Check URL for different modes and widget config
  // Parent sites pass these via query params when embedding the widget
  const widgetConfig = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    return {
      isWidgetDemo: params.get("mode") === "widget",
      isEmbed: params.get("embed") === "true",
      // Widget configuration props (passed by parent site)
      disclaimer: params.get("disclaimer") === "true",
      disclaimerText: params.get("disclaimerText") || "",
      autoOpen: params.get("autoOpen") !== "false", // Default true, can be disabled
      autoOpenDelay: parseInt(params.get("autoOpenDelay") || "5000", 10), // Default 5 seconds
    };
  }, []);

  const handleThemeChange = useCallback(
    (value: ColorScheme) => {
      setScheme(value);
    },
    [setScheme],
  );

  // Embed mode: Clean chat-only view for widget iframe
  if (widgetConfig.isEmbed) {
    return <EmbedView scheme={scheme} disclaimer={widgetConfig.disclaimer} disclaimerText={widgetConfig.disclaimerText} />;
  }

  // Widget demo: Full simulated website with floating chat
  if (widgetConfig.isWidgetDemo) {
    return (
      <WidgetDemo
        scheme={scheme}
        onThemeChange={handleThemeChange}
        autoOpen={widgetConfig.autoOpen}
        autoOpenDelay={widgetConfig.autoOpenDelay}
      />
    );
  }

  // Default: Full support dashboard
  return <Home scheme={scheme} onThemeChange={handleThemeChange} />;
}

