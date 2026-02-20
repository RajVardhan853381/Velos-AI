// Central API base URL.
// In dev, leave VITE_API_BASE unset so requests go through the Vite proxy
// (relative paths like /api/...) — this works from any host (localhost, LAN IP, etc).
// In production, set VITE_API_BASE to the deployed backend URL.
export const API_BASE = import.meta.env.VITE_API_BASE ?? '';
