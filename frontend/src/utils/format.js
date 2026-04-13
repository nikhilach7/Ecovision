export function percentage(value) {
  return `${Number(value).toFixed(1)}%`;
}

export function capitalize(word) {
  return word?.charAt(0).toUpperCase() + word?.slice(1);
}
