import { mapFeedPoint, mapLatestFeed, toNumber, toBinStatus } from "./utils";

const BASE_URL = "https://api.thingspeak.com/channels";
const CACHE_TTL_MS = 5000;

let cachedSnapshot = null;
let cachedAt = 0;
let inFlightPromise = null;

function buildUrl(endpoint) {
  const channelId = import.meta.env.VITE_THINGSPEAK_CHANNEL_ID;
  const readApiKey = import.meta.env.VITE_THINGSPEAK_READ_API_KEY;

  if (!channelId) {
    throw new Error("ThingSpeak channel is not configured");
  }

  const url = new URL(`${BASE_URL}/${channelId}/${endpoint}`);
  if (readApiKey) {
    url.searchParams.set("api_key", readApiKey);
  }
  return url.toString();
}

async function getJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`ThingSpeak request failed (${response.status})`);
  }
  return response.json();
}

function computeSummaryFromHistory(history, latest) {
  const wasteReadings = history.map((p) => toNumber(p?.wasteLevel, 0));
  const totalWaste = wasteReadings.reduce((sum, v) => sum + v, 0);

  const last10 = wasteReadings.slice(-10);
  const avgLast10 =
    last10.length > 0 ? last10.reduce((sum, v) => sum + v, 0) / Math.max(last10.length, 1) : 0;

  const latestWasteLevel = toNumber(latest?.wasteLevel, 0);

  return {
    totalWaste,
    fillLevel: toNumber(latest?.fillLevel, 0),
    binStatusRaw: toNumber(latest?.binStatus, 0),
    binStatusText: toBinStatus(latest?.binStatus),
    distance: toNumber(latest?.distance, 0),
    wasteLevelLatest: latestWasteLevel,
    wasteLevelAvg10: avgLast10,
  };
}

async function fetchSnapshotFromNetwork(results = 20) {
  const url = new URL(buildUrl("feeds.json"));
  url.searchParams.set("results", String(results));

  const data = await getJson(url.toString());
  const feeds = Array.isArray(data?.feeds) ? data.feeds : [];

  // Per project requirements: ThingSpeak fields are fixed:
  // field1 = Fill Level (%), field2 = Bin Status (0/1),
  // field3 = Distance (cm), field4 = Waste Level (%)
  const fieldMap = { fillLevel: "field1", binStatus: "field2", distance: "field3", wasteLevel: "field4" };

  const history = feeds.map((feed, index) => mapFeedPoint(feed, index, fieldMap));
  const latestRaw = feeds.at(-1);
  const latest = mapLatestFeed(latestRaw, fieldMap);
  const summary = computeSummaryFromHistory(history, latest);

  return {
    latest,
    history,
    summary,
    fetchedAt: new Date().toISOString(),
  };
}

export async function fetchThingSpeakSnapshot({ results = 20, force = false } = {}) {
  const now = Date.now();
  const isCacheFresh = cachedSnapshot && now - cachedAt < CACHE_TTL_MS;

  if (!force && isCacheFresh) {
    return cachedSnapshot;
  }

  if (inFlightPromise) {
    return inFlightPromise;
  }

  inFlightPromise = fetchSnapshotFromNetwork(results)
    .then((snapshot) => {
      cachedSnapshot = snapshot;
      cachedAt = Date.now();
      return snapshot;
    })
    .finally(() => {
      inFlightPromise = null;
    });

  return inFlightPromise;
}
