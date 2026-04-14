import QueryPanel from "../components/QueryPanel";
import UploadPanel from "../components/UploadPanel";
import WastePieChart from "../components/WastePieChart";

export default function ClassificationPage({ dashboard, onUploaded }) {
  return (
    <section className="grid gap-4 lg:grid-cols-3">
      <div className="space-y-4 lg:col-span-2">
        <UploadPanel onUploaded={onUploaded} />
        <QueryPanel />
      </div>
      <div className="lg:col-span-1">
        <WastePieChart distribution={dashboard.distribution} />
      </div>
    </section>
  );
}
