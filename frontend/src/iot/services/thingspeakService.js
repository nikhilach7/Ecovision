const BASE_URL = "https://api.thingspeak.com/channels";

function getChannelConfig() {
  const channelId = import.meta.env.VITE_THINGSPEAK_CHANNEL_ID;
  const readApiKey = import.meta.env.VITE_THINGSPEAK_READ_API_KEY;
  if (!channelId) {
    throw new Error("ThingSpeak channel is not configured");
  }
  return { channelId, readApiKey };
}

function buildUrl(endpoint, params = {}) {
  const { channelId, readApiKey } = getChannelConfig();
  const url = new URL(`${BASE_URL}/${channelId}/${endpoint}`);
  if (readApiKey) {
    url.searchParams.set("api_key", readApiKey);
  }
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

function toNumber(value, fallback = 0) {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

function normalizeFieldMap(channel) {
  const byName = [
    ["field1", channel?.field1],
    ["field2", channel?.field2],
    ["field3", channel?.field3],
    ["field4", channel?.field4],
  ];
  const byLabel = (matcher, fallback) => {
    const match = byName.find(([, label]) => matcher(String(label || "").toLowerCase()));
    return match ? match[0] : fallback;
  };

  return {
    fillLevel: byLabel((label) => label.includes("fill"), "field1"),
    binStatus: byLabel((label) => label.includes("status"), "field2"),
    distance: byLabel((label) => label.includes("distance"), "field3"),
    wasteLevel: byLabel((label) => label.includes("waste"), "field4"),
  };
}

function normalizeFeed(feed, fieldMap) {
  return {
    fillLevel: toNumber(feed?.[fieldMap.fillLevel], 0),
    binStatus: toNumber(feed?.[fieldMap.binStatus], 0),
    distance: toNumber(feed?.[fieldMap.distance], 0),
    wasteLevel: toNumber(feed?.[fieldMap.wasteLevel], 0),
    timestamp: feed?.created_at || "",
  };
}

async function fetchWithRetry(url, retries = 1) {
  let lastError;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      const response = await fetch(url, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`ThingSpeak request failed (${response.status})`);
      }
      return await response.json();
    } catch (error) {
      lastError = error;
      if (attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    }
  }
  throw lastError || new Error("ThingSpeak request failed");
}

export async function fetchThingSpeakHistory(results = 20) {
  const data = await fetchWithRetry(buildUrl("feeds.json", { results }), 1);
  console.log("ThingSpeak Response:", data);

  const feeds = Array.isArray(data?.feeds) ? data.feeds : [];
  const fieldMap = normalizeFieldMap(data?.channel);
  const normalizedFeeds = feeds.map((feed) => normalizeFeed(feed, fieldMap));
  console.log("Parsed feeds:", normalizedFeeds);
  return normalizedFeeds;
}

export async function fetchThingSpeakLatest() {
  const data = await fetchWithRetry(buildUrl("feeds/last.json"), 1);
  console.log("ThingSpeak Response:", data);

  const fieldMap = normalizeFieldMap();
  const latest = normalizeFeed(data, fieldMap);
  console.log("Parsed feeds:", latest);
  return latest;
}

export function buildHourlyWasteTrend(feeds) {
  const groups = new Map();
  feeds.forEach((feed) => {
    const ts = feed?.timestamp || feed?.createdAt || "";
    if (!ts) {
      return;
    }
    const date = new Date(ts);
    if (Number.isNaN(date.getTime())) {
      return;
    }
    const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
    const current = groups.get(key) || { total: 0, count: 0, hourLabel: date };
    current.total += toNumber(feed.wasteLevel, 0);
    current.count += 1;
    groups.set(key, current);
  });

  return Array.from(groups.values()).map((item) => ({
    hour: item.hourLabel.toLocaleTimeString([], { hour: "numeric" }),
    count: Number((item.total / Math.max(item.count, 1)).toFixed(2)),
  }));
}

