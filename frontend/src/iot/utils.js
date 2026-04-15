export function toNumber(value, fallback = 0) {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

export function toBinStatus(value) {
  const status = toNumber(value, 0);
  return status >= 1 ? "Full 🚨" : "Normal 🟢";
}

export function hasThingSpeakConfig() {
  return Boolean(import.meta.env.VITE_THINGSPEAK_CHANNEL_ID);
}

function fieldKeyByLabel(channel, predicate, fallbackKey) {
  if (!channel) {
    return fallbackKey;
  }
  const pairs = [
    ["field1", channel.field1],
    ["field2", channel.field2],
    ["field3", channel.field3],
    ["field4", channel.field4],
  ];
  const found = pairs.find(([, label]) => predicate(String(label || "").toLowerCase()));
  return found ? found[0] : fallbackKey;
}

export function resolveFieldMap(channel) {
  return {
    fillLevel: fieldKeyByLabel(channel, (label) => label.includes("fill"), "field1"),
    binStatus: fieldKeyByLabel(channel, (label) => label.includes("status"), "field2"),
    distance: fieldKeyByLabel(channel, (label) => label.includes("distance"), "field3"),
    wasteLevel: fieldKeyByLabel(channel, (label) => label.includes("waste"), "field4"),
  };
}

export function mapFeedPoint(feed, index, fieldMap = resolveFieldMap()) {
  return {
    index: index + 1,
    createdAt: feed?.created_at || `#${index + 1}`,
    fillLevel: toNumber(feed?.[fieldMap.fillLevel], 0),
    binStatus: toNumber(feed?.[fieldMap.binStatus], 0),
    distance: toNumber(feed?.[fieldMap.distance], 0),
    wasteLevel: toNumber(feed?.[fieldMap.wasteLevel], 0),
  };
}

export function mapLatestFeed(feed, fieldMap = resolveFieldMap()) {
  return {
    fillLevel: toNumber(feed?.[fieldMap.fillLevel], 0),
    binStatus: toNumber(feed?.[fieldMap.binStatus], 0),
    distance: toNumber(feed?.[fieldMap.distance], 0),
    wasteLevel: toNumber(feed?.[fieldMap.wasteLevel], 0),
    updatedAt: feed?.created_at || null,
  };
}
