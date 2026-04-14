import { Cloud, HardDrive, Waves } from "lucide-react";
import FillLevelCard from "../components/FillLevelCard";
import StatCard from "../components/StatCard";

export default function MonitoringPage({ dashboard }) {
  return (
    <section className="space-y-4">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Latest Fill"
          value={`${Math.round(dashboard.latest_fill_percentage || 0)}%`}
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

      <FillLevelCard fill={dashboard.latest_fill_percentage} location={dashboard.latest_location} />
    </section>
  );
}
