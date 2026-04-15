import { useEffect, useState } from "react";
import TopNavbar from "./components/TopNavbar";
import LoginPage from "./pages/LoginPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import ClassificationPage from "./pages/ClassificationPage";
import HomePage from "./pages/HomePage";
import MonitoringPage from "./pages/MonitoringPage";
import { clearAuthToken, fetchDashboard, getAuthToken, getCurrentUser, login, register, setAuthToken } from "./services/api";
import { mockDashboard } from "./utils/mockData";
import { IoTDataProvider } from "./iot/IoTDataContext";

export default function App() {
  const [activePage, setActivePage] = useState("home");
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [dashboard, setDashboard] = useState(mockDashboard);
  const [offlineMode, setOfflineMode] = useState(true);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("ecovision-theme") || "dark";
  });

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
    setActivePage("home");
  };

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    localStorage.setItem("ecovision-theme", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
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
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    if (!authenticated) return;
    loadDashboard();
    const timer = setInterval(loadDashboard, 8000);
    return () => clearInterval(timer);
  }, [authenticated]);

  if (!authenticated) {
    return <LoginPage onLogin={handleAuth} />;
  }

  const renderPage = () => {
    if (activePage === "analytics") {
      return <AnalyticsPage dashboard={dashboard} />;
    }

    if (activePage === "monitoring") {
      return <MonitoringPage dashboard={dashboard} />;
    }

    if (activePage === "classification") {
      return <ClassificationPage dashboard={dashboard} onUploaded={loadDashboard} />;
    }

    return <HomePage dashboard={dashboard} offlineMode={offlineMode} />;
  };

  return (
    <IoTDataProvider refreshMs={5000}>
      <main className="min-h-screen w-full bg-[var(--bg-main)] text-[var(--text-main)]">
        <div className="flex min-h-screen flex-col">
          <TopNavbar
            userName={user?.full_name || "Operator"}
            offlineMode={offlineMode}
            location={dashboard.latest_location}
            onLogout={handleLogout}
            onThemeToggle={toggleTheme}
            theme={theme}
            activePage={activePage}
            onNavigate={setActivePage}
          />
  
          <div className="flex-1 px-4 py-5 md:px-6 md:py-6 xl:px-8">
            <div className="mx-auto w-full max-w-[1400px]">
              {offlineMode && (
                <div className="mb-5 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-300">
                  Backend/hardware not reachable. Showing demo fallback data.
                </div>
              )}
  
              {renderPage()}
            </div>
          </div>
  
          <footer className="border-t border-[var(--line)] bg-[var(--topbar-bg)]/88 px-4 py-3 text-sm text-[var(--text-soft)] md:px-6">
            <div className="mx-auto flex w-full max-w-[1400px] items-center justify-between gap-2">
              <span>EcoVision AI</span>
              <span className="text-xs text-[var(--text-muted)]">
                Smart waste monitoring and classification dashboard
              </span>
            </div>
          </footer>
        </div>
      </main>
    </IoTDataProvider>
  );
}
