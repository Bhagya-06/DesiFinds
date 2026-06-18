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

export function getWishlist(): string[] {
  try {
    const stored = localStorage.getItem("desifinds_wishlist");
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function toggleWishlist(productId: string): boolean {
  try {
    const wishlist = getWishlist();
    const idx = wishlist.indexOf(productId);
    const updated = idx >= 0 ? wishlist.filter((id) => id !== productId) : [...wishlist, productId];
    localStorage.setItem("desifinds_wishlist", JSON.stringify(updated));
    return updated.includes(productId);
  } catch {
    return false;
  }
}

export function isWishlisted(productId: string): boolean {
  return getWishlist().includes(productId);
}

export function getApiKey(): string {
  try { return localStorage.getItem("desifinds_api_key") || ""; } catch { return ""; }
}

export function setApiKey(key: string): void {
  try { localStorage.setItem("desifinds_api_key", key); } catch { /* ignore */ }
}
