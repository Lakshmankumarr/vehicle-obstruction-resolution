/**
 * FreeWay Community — Card Component
 */
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors, radius, shadows } from '../theme';

export function Card({ children, style, noPadding = false, elevated = true }) {
  return (
    <View style={[styles.card, elevated && shadows.card, noPadding && styles.noPad, style]}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.cardBorder,
  },
  noPad: { padding: 0, overflow: 'hidden' },
});
