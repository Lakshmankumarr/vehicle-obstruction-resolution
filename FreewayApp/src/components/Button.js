/**
 * FreeWay Community — Reusable Button Component
 * Variants: primary, secondary, danger, ghost, outline
 */
import React from 'react';
import {
  TouchableOpacity,
  Text,
  ActivityIndicator,
  StyleSheet,
  View,
} from 'react-native';
import { colors, radius, spacing, shadows } from '../theme';

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon = null,
  fullWidth = true,
  style,
}) {
  const isDisabled = disabled || loading;

  const containerStyle = [
    styles.base,
    styles[variant],
    styles[`size_${size}`],
    fullWidth && styles.fullWidth,
    isDisabled && styles.disabled,
    variant === 'primary' && shadows.button,
    variant === 'danger' && shadows.danger,
    style,
  ];

  const textStyle = [
    styles.text,
    styles[`text_${variant}`],
    styles[`textSize_${size}`],
  ];

  return (
    <TouchableOpacity
      style={containerStyle}
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === 'primary' || variant === 'danger' ? '#fff' : colors.primary}
          size="small"
        />
      ) : (
        <View style={styles.row}>
          {icon && <View style={styles.iconWrap}>{icon}</View>}
          <Text style={textStyle}>{title}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  fullWidth: { width: '100%' },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  iconWrap: { marginRight: spacing.sm },

  // Variants
  primary: { backgroundColor: colors.primary },
  secondary: { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.cardBorder },
  danger: { backgroundColor: colors.danger },
  ghost: { backgroundColor: 'transparent' },
  outline: { backgroundColor: 'transparent', borderWidth: 1.5, borderColor: colors.primary },

  // Sizes
  size_sm: { paddingVertical: 8, paddingHorizontal: 16 },
  size_md: { paddingVertical: 14, paddingHorizontal: 20 },
  size_lg: { paddingVertical: 18, paddingHorizontal: 24 },

  // Text colors by variant
  text: { fontWeight: '600', letterSpacing: 0.3 },
  text_primary: { color: '#fff' },
  text_secondary: { color: colors.textPrimary },
  text_danger: { color: '#fff' },
  text_ghost: { color: colors.primary },
  text_outline: { color: colors.primary },

  // Text size by size
  textSize_sm: { fontSize: 13 },
  textSize_md: { fontSize: 15 },
  textSize_lg: { fontSize: 17 },

  // Disabled
  disabled: { opacity: 0.5 },
});
