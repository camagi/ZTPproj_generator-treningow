const RENDER_API_URL = "https://ztpproj-generator-treningow.onrender.com/api";
const RENDER_STATIC_URL = "https://ztpproj-generator-treningow.onrender.com/exercises-static";

function configuredValue(value: string | undefined, fallback: string) {
  const normalized = value?.trim();
  return normalized && normalized !== "undefined" ? normalized : fallback;
}

function isLocalBrowser() {
  if (typeof window === "undefined") return true;
  return ["localhost", "127.0.0.1", "0.0.0.0"].includes(window.location.hostname);
}

function runtimeDefault(localPath: string, productionUrl: string) {
  return isLocalBrowser() ? localPath : productionUrl;
}

export const API_URL = configuredValue(
  process.env.NEXT_PUBLIC_API_URL,
  runtimeDefault("/api", RENDER_API_URL),
);

export const STATIC_URL = configuredValue(
  process.env.NEXT_PUBLIC_STATIC_URL,
  runtimeDefault("/exercises-static", RENDER_STATIC_URL),
);
