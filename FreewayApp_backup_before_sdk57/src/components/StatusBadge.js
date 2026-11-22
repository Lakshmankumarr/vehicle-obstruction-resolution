/**
 * FreeWay Community — StatusBadge Component
 * Displays colored status pill for request states.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius } from '../theme';

const STATUS_CONFIG = {
  PENDING:    { label: 'Pending',    bg: colors.warningBg,  text: colors.warning,  dot: colors.warning },
  NOTIFIED:   { label: 'Notified',   bg: colors.infoBg,     text: colors.info,     dot: colors.info },
  ACKNOWLEDGED:{ label: 'Ack\'d',    bg: colors.infoBg,     text: colors.info,     dot: colors.info },
  MOVING:     { label: 'Moving',     bg: colors.successBg,  text: colors.success,  dot: colors.success },
  RESOLVED:   { label: 'Resolved',   bg: colors.successBg,  text: colors.success,  dot: colors.success },
  CANCELLED:  { label: 'Cancelled',  bg: colors.dangerBg,   text: colors.danger,   dot: colors.danger },
  EXPIRED:    { label: 'Expired',    bg: colors.dangerBg,   text: colors.danger,   dot: colors.danger },
  EMERGENCY:  { label: '⚡ Emergency',bg: colors.dangerBg,  text: colors.danger,   dot: colors.danger },
};

export function StatusBadge({ status, style }) {
  const cfg = STATUS_CONFIG[status] || { label: status, bg: colors.card, text: colors.textSecondary, dot: colors.textMuted };
  return (
    <View style={[styles.badge, { backgroundColor: cfg.bg }, style]}>
      <View style={[styles.dot, { backgroundColor: cfg.dot }]} />
      <Text style={[styles.text, { color: cfg.text }]}>{cfg.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radius.full,
    alignSelf: 'flex-start',
  },
  dot: { width: 6, height: 6, borderRadius: 3, marginRight: 6 },
  text: { fontSize: 12, fontWeight: '600' },
});
