import { useEffect, useState } from "react";
import { Activity, Cloud, Database, HardDrive, Recycle } from "lucide-react";
import FillLevelCard from "./components/FillLevelCard";
import HeaderBar from "./components/HeaderBar";
import QueryPanel from "./components/QueryPanel";
import StatCard from "./components/StatCard";
import TrendLineChart from "./components/TrendLineChart";
import UploadPanel from "./components/UploadPanel";
import WastePieChart from "./components/WastePieChart";
import LoginPage from "./pages/LoginPage";
import { clearAuthToken, fetchDashboard, getAuthToken, getCurrentUser, login, register, setAuthToken } from "./services/api";
import { mockDashboard } from "./utils/mockData";

export default function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [dashboard, setDashboard] = useState(mockDashboard);
  const [offlineMode, setOfflineMode] = useState(true);

  const handleAuth = async ({ mode, fullName, email, password }) => {
    const response =
      mode === "login" ? await login(email, password) : await register(fullName, email, password);
    setAuthToken(response.access_token);
    setUser(response.user);
    setAuthenticated(true);
  };

  const handleLogout = () => {
    clearAuthToken();
    setAuthenticated(false);
    setUser(null);
  };

  const loadDashboard = async () => {
    try {
      const data = await fetchDashboard();
      setDashboard(data);
      setOfflineMode(false);
    } catch {
      setDashboard(mockDashboard);
      setOfflineMode(true);
    }
  };

  useEffect(() => {
    const token = getAuthToken();
    if (!token) return;

    getCurrentUser()
      .then((profile) => {
        setUser(profile);
        setAuthenticated(true);
      })
      .catch(() => {
        clearAuthToken();
        setAuthenticated(false);
      });
  }, []);

  useEffect(() => {
    if (!authenticated) return;
    loadDashboard();
    const timer = setInterval(loadDashboard, 8000);
    return () => clearInterval(timer);
  }, [authenticated]);

  if (!authenticated) {
    return <LoginPage onLogin={handleAuth} />;
  }

  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-4 py-6 md:px-8">
      <HeaderBar
        location={dashboard.latest_location}
        full={dashboard.is_bin_full}
        userName={user?.full_name || "Operator"}
        onLogout={handleLogout}
      />

      {offlineMode && (
        <div className="mb-6 rounded-xl border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">
          Backend/hardware not reachable. Showing demo fallback data.
        </div>
      )}

      <section className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Waste"
          value={dashboard.total_waste_items}
          subtitle="Classified waste images"
          icon={Recycle}
          tone="green"
        />
        <StatCard
          title="Active Data Feed"
          value={offlineMode ? "Simulated" : "Live"}
          subtitle="Sensor + AI pipeline status"
          icon={Activity}
          tone="blue"
        />
        <StatCard
          title="Database"
          value={dashboard.cloud_provider || "MongoDB"}
          subtitle="Cloud database and telemetry logs"
          icon={Database}
          tone="amber"
        />
        <StatCard
          title="Cloud Storage"
          value={dashboard.storage_backend === "gridfs" ? `${dashboard.cloud_storage_mb} MB` : "Local"}
          subtitle={
            dashboard.storage_backend === "gridfs"
              ? `${dashboard.cloud_images_count} images synced to cloud`
              : "Switch STORAGE_BACKEND to gridfs"
          }
          icon={Cloud}
          tone="blue"
        />
        <StatCard
          title="Storage Mode"
          value={dashboard.storage_backend?.toUpperCase() || "LOCAL"}
          subtitle="Atlas GridFS recommended for free cloud demos"
          icon={HardDrive}
          tone="green"
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <div className="grid gap-4 md:grid-cols-2">
            <WastePieChart distribution={dashboard.distribution} />
            <FillLevelCard fill={dashboard.latest_fill_percentage} location={dashboard.latest_location} />
          </div>
          <TrendLineChart trend={dashboard.daily_trend} />
        </div>

        <div className="space-y-4">
          <UploadPanel onUploaded={loadDashboard} />
          <QueryPanel />
        </div>
      </section>
    </main>
  );
}
