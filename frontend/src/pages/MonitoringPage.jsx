import { Cloud, HardDrive, Waves } from "lucide-react";
import FillLevelCard from "../components/FillLevelCard";
import StatCard from "../components/StatCard";
import IoTLivePanel from "../iot/IoTLivePanel";
import { useIoTData } from "../iot/IoTDataContext";

export default function MonitoringPage({ dashboard }) {
  const { latest, loading, error } = useIoTData();
  const latestFill = Math.round(latest?.fillLevel ?? 0);

  return (
    <section className="space-y-4">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Latest Fill"
          value={loading ? "Loading..." : `${latestFill}%`}
          subtitle="Real-time occupancy"
          icon={Waves}
          tone="blue"
        />
        <StatCard
          title="Cloud Storage"
          value={dashboard.storage_backend === "gridfs" ? `${dashboard.cloud_storage_mb} MB` : "Local"}
          subtitle={dashboard.storage_backend === "gridfs" ? `${dashboard.cloud_images_count} images synced` : "Switch STORAGE_BACKEND to gridfs"}
          icon={Cloud}
          tone="amber"
        />
        <StatCard
          title="Storage Mode"
          value={dashboard.storage_backend?.toUpperCase() || "LOCAL"}
          subtitle="Current image retention strategy"
          icon={HardDrive}
          tone="green"
        />
      </div>

      <FillLevelCard fill={latest?.fillLevel ?? 0} location={dashboard.latest_location} />

      <div className="panel p-5">
        <h3 className="font-title text-xl font-semibold text-[var(--text-main)]">Live IoT Monitoring</h3>
        <p className="mt-1 text-sm text-[var(--text-soft)]">
          Real-time ThingSpeak feed auto-refreshing every 5 seconds.
        </p>
      </div>
      <IoTLivePanel latest={latest} loading={loading} error={error} />
    </section>
  );
}
