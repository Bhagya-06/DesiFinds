import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(price);
}

export function getRecentSearches(): string[] {
  try {
    const stored = localStorage.getItem("desifinds_recent_searches");
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function addRecentSearch(query: string): void {
  try {
    const searches = getRecentSearches().filter((s) => s !== query);
    const updated = [query, ...searches].slice(0, 8);
    localStorage.setItem("desifinds_recent_searches", JSON.stringify(updated));
  } catch { /* ignore */ }
}

export function getWishlist(username?: string): string[] {
  try {
    const userKey = username ? `desifinds_wishlist_${username.toLowerCase().trim()}` : "desifinds_wishlist";
    const stored = localStorage.getItem(userKey);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function toggleWishlist(productId: string, username?: string): boolean {
  try {
    const userKey = username ? `desifinds_wishlist_${username.toLowerCase().trim()}` : "desifinds_wishlist";
    const wishlist = getWishlist(username);
    const idx = wishlist.indexOf(productId);
    const updated = idx >= 0 ? wishlist.filter((id) => id !== productId) : [...wishlist, productId];
    localStorage.setItem(userKey, JSON.stringify(updated));
    return updated.includes(productId);
  } catch {
    return false;
  }
}

export function isWishlisted(productId: string, username?: string): boolean {
  return getWishlist(username).includes(productId);
}

export function getApiKey(): string {
  try { return localStorage.getItem("desifinds_api_key") || ""; } catch { return ""; }
}

export function setApiKey(key: string): void {
  try { localStorage.setItem("desifinds_api_key", key); } catch { /* ignore */ }
}
