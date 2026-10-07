/**
 * FreeWay Community — Reusable Input Component
 * Styled text input with label, error, and icon support.
 */
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { colors, radius, spacing } from '../theme';

export function Input({
  label,
  value,
  onChangeText,
  placeholder,
  secureTextEntry = false,
  keyboardType = 'default',
  autoCapitalize = 'none',
  error,
  icon = null,
  rightIcon = null,
  onRightIconPress,
  style,
  ...rest
}) {
  const [focused, setFocused] = useState(false);
  const [secure, setSecure] = useState(secureTextEntry);

  return (
    <View style={[styles.wrapper, style]}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View
        style={[
          styles.inputRow,
          focused && styles.inputRowFocused,
          error && styles.inputRowError,
        ]}
      >
        {icon && <View style={styles.leftIcon}>{icon}</View>}
        <TextInput
          style={[styles.input, icon && styles.inputWithIcon]}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={colors.textMuted}
          secureTextEntry={secure}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          {...rest}
        />
        {secureTextEntry && (
          <TouchableOpacity
            style={styles.rightIcon}
            onPress={() => setSecure(!secure)}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            <Text style={styles.toggleText}>{secure ? '👁' : '🙈'}</Text>
          </TouchableOpacity>
        )}
        {rightIcon && !secureTextEntry && (
          <TouchableOpacity
            style={styles.rightIcon}
            onPress={onRightIconPress}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            {rightIcon}
          </TouchableOpacity>
        )}
      </View>
      {error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { marginBottom: spacing.md },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.textSecondary,
    marginBottom: 6,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.inputBg,
    borderRadius: radius.md,
    borderWidth: 1.5,
    borderColor: colors.inputBorder,
  },
  inputRowFocused: { borderColor: colors.inputBorderFocus },
  inputRowError: { borderColor: colors.danger },
  leftIcon: { paddingLeft: spacing.md },
  rightIcon: { paddingRight: spacing.md },
  input: {
    flex: 1,
    color: colors.textPrimary,
    fontSize: 15,
    paddingVertical: 14,
    paddingHorizontal: spacing.md,
  },
  inputWithIcon: { paddingLeft: spacing.sm },
  toggleText: { fontSize: 16 },
  error: { fontSize: 12, color: colors.danger, marginTop: 4, marginLeft: 2 },
});
