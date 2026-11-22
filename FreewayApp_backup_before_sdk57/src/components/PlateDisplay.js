/**
 * FreeWay Community — PlateDisplay Component
 * Renders an Indian-style number plate with state code strip.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius } from '../theme';

export function PlateDisplay({ plate, size = 'md', style }) {
  const isLarge = size === 'lg';
  const fontSize = isLarge ? 28 : size === 'sm' ? 16 : 22;

  return (
    <View style={[styles.plate, isLarge && styles.plateLarge, style]}>
      {/* IND Strip */}
      <View style={[styles.strip, isLarge && styles.stripLarge]}>
        <Text style={[styles.stripText, isLarge && { fontSize: 10 }]}>🇮🇳 IND</Text>
      </View>
      {/* Plate Number */}
      <Text style={[styles.plateText, { fontSize }]}>{plate || 'XX-00-XX-0000'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  plate: {
    backgroundColor: colors.plateBackground,
    borderRadius: radius.sm,
    borderWidth: 2,
    borderColor: colors.plateBorder,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    alignSelf: 'flex-start',
  },
  plateLarge: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: radius.md,
    borderWidth: 3,
  },
  strip: {
    backgroundColor: colors.plateStrip,
    borderRadius: 4,
    paddingHorizontal: 4,
    paddingVertical: 2,
    marginRight: 8,
  },
  stripLarge: { paddingHorizontal: 6, paddingVertical: 4, marginRight: 12 },
  stripText: { color: '#fff', fontSize: 8, fontWeight: '700', letterSpacing: 0.5 },
  plateText: {
    color: colors.plateText,
    fontWeight: '900',
    letterSpacing: 3,
    fontFamily: 'monospace',
  },
});
