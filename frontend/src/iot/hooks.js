import { useCallback, useEffect, useState } from "react";
import { fetchThingSpeakHistory, fetchThingSpeakLatest } from "./api";
import { hasThingSpeakConfig } from "./utils";

export function useThingSpeakLatest(refreshMs = 8000) {
  const [latest, setLatest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadLatest = useCallback(async () => {
    if (!hasThingSpeakConfig()) {
      setLoading(false);
      setError("ThingSpeak channel is not configured");
      return;
    }
    try {
      const data = await fetchThingSpeakLatest();
      setLatest(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch latest IoT data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLatest();
    const timer = setInterval(loadLatest, refreshMs);
    return () => clearInterval(timer);
  }, [loadLatest, refreshMs]);

  return { latest, loading, error, reload: loadLatest };
}

export function useThingSpeakHistory(results = 20, refreshMs = 10000) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadHistory = useCallback(async () => {
    if (!hasThingSpeakConfig()) {
      setLoading(false);
      setError("ThingSpeak channel is not configured");
      return;
    }
    try {
      const data = await fetchThingSpeakHistory(results);
      setHistory(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch IoT history");
    } finally {
      setLoading(false);
    }
  }, [results]);

  useEffect(() => {
    loadHistory();
    const timer = setInterval(loadHistory, refreshMs);
    return () => clearInterval(timer);
  }, [loadHistory, refreshMs]);

  return { history, loading, error, reload: loadHistory };
}
