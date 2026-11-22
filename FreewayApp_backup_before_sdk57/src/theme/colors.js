/**
 * FreeWay Community Design System Colors & Theme Tokens.
 * Modern Dark Mode Aesthetic with Electric Indigo & Cyan Accents.
 */

export const colors = {
  // Backgrounds
  background: "#0B0F19",
  backgroundSecondary: "#111827",
  card: "#1F2937",
  cardBorder: "rgba(255, 255, 255, 0.08)",
  cardHover: "#283548",

  // Brand Accents
  primary: "#3B82F6",
  primaryGradient: ["#3B82F6", "#2563EB"],
  accent: "#06B6D4",
  accentGlow: "rgba(6, 182, 212, 0.25)",

  // Status Colors
  success: "#10B981",
  successBg: "rgba(16, 185, 129, 0.15)",
  warning: "#F59E0B",
  warningBg: "rgba(245, 158, 11, 0.15)",
  danger: "#EF4444",
  dangerBg: "rgba(239, 68, 68, 0.15)",
  info: "#6366F1",
  infoBg: "rgba(99, 102, 241, 0.15)",

  // Typography
  textPrimary: "#F9FAFB",
  textSecondary: "#9CA3AF",
  textMuted: "#6B7280",
  textInverse: "#0B0F19",

  // Indian Plate Theme (IND blue banner with retro-reflective yellow/white plate)
  plateBackground: "#F8FAFC",
  plateText: "#0F172A",
  plateBorder: "#CBD5E1",
  plateStrip: "#1E40AF",

  // Components
  inputBg: "#1E293B",
  inputBorder: "#334155",
  inputBorderFocus: "#3B82F6",
  divider: "rgba(255, 255, 255, 0.06)",
};

export const typography = {
  titleLarge: { fontSize: 28, fontWeight: "700", color: colors.textPrimary },
  titleMedium: { fontSize: 22, fontWeight: "600", color: colors.textPrimary },
  titleSmall: { fontSize: 18, fontWeight: "600", color: colors.textPrimary },
  bodyLarge: { fontSize: 16, fontWeight: "400", color: colors.textPrimary },
  bodyMedium: { fontSize: 14, fontWeight: "400", color: colors.textSecondary },
  bodySmall: { fontSize: 12, fontWeight: "400", color: colors.textMuted },
  plateNumber: { fontSize: 22, fontWeight: "800", letterSpacing: 2, color: colors.plateText },
};
