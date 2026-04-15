import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { fetchThingSpeakSnapshot } from "./api";
import { buildHourlyWasteTrend } from "./services/thingspeakService";

const IoTDataContext = createContext(null);

export function IoTDataProvider({ children, refreshMs = 5000 }) {
  const [latest, setLatest] = useState({ fillLevel: 0, binStatus: 0, distance: 0, wasteLevel: 0, updatedAt: null });
  const [history, setHistory] = useState([]);
  const [summary, setSummary] = useState({
    totalWaste: 0,
    fillLevel: 0,
    binStatusRaw: 0,
    binStatusText: "Normal 🟢",
    distance: 0,
    wasteLevelLatest: 0,
    wasteLevelAvg10: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const loadIoTData = async () => {
      try {
        const snapshot = await fetchThingSpeakSnapshot({ results: 20 });
        if (!isMounted) {
          return;
        }
        setHistory(snapshot.history || []);
        setLatest(snapshot.latest || { fillLevel: 0, binStatus: 0, distance: 0, wasteLevel: 0, updatedAt: null });
        setSummary(
          snapshot.summary || {
            totalWaste: 0,
            fillLevel: 0,
            binStatusRaw: 0,
            binStatusText: "Normal 🟢",
            distance: 0,
            wasteLevelLatest: 0,
            wasteLevelAvg10: 0,
          },
        );
        setLastUpdatedAt(snapshot.fetchedAt || new Date().toISOString());
        setError("");
      } catch (err) {
        if (!isMounted) {
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to fetch IoT data");
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadIoTData();
    const timer = setInterval(loadIoTData, refreshMs);
    return () => {
      isMounted = false;
      clearInterval(timer);
    };
  }, [refreshMs]);

  const hourlyWasteTrend = useMemo(() => buildHourlyWasteTrend(history), [history]);

  const value = useMemo(
    () => ({
      latest,
      history,
      summary,
      hourlyWasteTrend,
      loading,
      error,
      lastUpdatedAt,
    }),
    [latest, history, summary, hourlyWasteTrend, loading, error, lastUpdatedAt],
  );

  return <IoTDataContext.Provider value={value}>{children}</IoTDataContext.Provider>;
}

export function useIoTData() {
  const context = useContext(IoTDataContext);
  if (!context) {
    throw new Error("useIoTData must be used inside IoTDataProvider");
  }
  return context;
}

