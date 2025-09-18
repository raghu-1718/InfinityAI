// Central API configuration for frontend
// Uses REACT_APP_API_URL when provided; otherwise falls back to same-origin '/api' or localhost in dev.

const envApi = process.env.REACT_APP_API_URL?.trim();

// If running under a custom domain with a reverse proxy, you can set REACT_APP_API_URL to absolute URL
// e.g., https://api.infinityai.pro or https://www.infinityai.pro
export const API_BASE: string = envApi ||
  (typeof window !== 'undefined'
    ? `${window.location.origin.replace(/\/$/, '')}`
    : 'http://localhost:8000');

export function apiUrl(path: string): string {
  const base = API_BASE.replace(/\/$/, '');
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${base}${p}`;
}

export function wsUrl(path: string): string {
  const loc = typeof window !== 'undefined' ? window.location : { protocol: 'http:', host: 'localhost:8000' } as any;
  const base = envApi || `${loc.protocol}//${loc.host}`;
  const wsBase = base.replace(/^http/i, loc.protocol === 'https:' ? 'wss' : 'ws');
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${wsBase}${p}`;
}

export default {
  API_BASE,
  apiUrl,
  wsUrl,
};
