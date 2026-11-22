/**
 * FreeWay Community — LoginScreen
 * Dark-mode premium login with animated gradient header.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, KeyboardAvoidingView,
  Platform, TouchableOpacity, Alert,
} from 'react-native';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { colors, spacing, radius } from '../../theme';

export default function LoginScreen({ navigation }) {
  const { login } = useAuth();
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const e = {};
    if (!vehicleNumber.trim()) e.vehicleNumber = 'Vehicle number is required';
    if (!password) e.password = 'Password is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleLogin = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      await login(vehicleNumber.trim().toUpperCase(), password);
      // Navigation handled by AppNavigator watching isAuthenticated
    } catch (err) {
      Alert.alert('Login Failed', err.message || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Hero Header */}
        <View style={styles.hero}>
          <View style={styles.logoWrap}>
            <Text style={styles.logoIcon}>🚗</Text>
            <View style={styles.logoDot} />
          </View>
          <Text style={styles.appName}>FreeWay Community</Text>
          <Text style={styles.tagline}>Privacy-first vehicle obstruction resolution</Text>
        </View>

        {/* Form Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Welcome back</Text>
          <Text style={styles.cardSubtitle}>Sign in with your vehicle number</Text>

          <Input
            label="Vehicle Number"
            value={vehicleNumber}
            onChangeText={setVehicleNumber}
            placeholder="MH-12-AB-1234"
            autoCapitalize="characters"
            error={errors.vehicleNumber}
            style={styles.inputSpacing}
          />

          <Input
            label="Password"
            value={password}
            onChangeText={setPassword}
            placeholder="Enter your password"
            secureTextEntry
            error={errors.password}
          />

          <Button
            title="Sign In"
            onPress={handleLogin}
            loading={loading}
            size="lg"
            style={styles.loginBtn}
          />

          <View style={styles.divider}>
            <View style={styles.line} />
            <Text style={styles.dividerText}>or</Text>
            <View style={styles.line} />
          </View>

          <TouchableOpacity
            style={styles.registerLink}
            onPress={() => navigation.navigate('Register')}
          >
            <Text style={styles.registerLinkText}>
              New here?{' '}
              <Text style={styles.registerLinkBold}>Create an account →</Text>
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.footer}>
          🔒 Your identity is always protected. We never share your personal data.
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  scroll: { flexGrow: 1, padding: spacing.lg },

  hero: { alignItems: 'center', paddingTop: spacing.xxl, paddingBottom: spacing.xl },
  logoWrap: { position: 'relative', marginBottom: spacing.md },
  logoIcon: { fontSize: 60 },
  logoDot: {
    position: 'absolute',
    bottom: 2,
    right: -4,
    width: 16,
    height: 16,
    backgroundColor: colors.accent,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: colors.background,
  },
  appName: {
    fontSize: 26,
    fontWeight: '800',
    color: colors.textPrimary,
    letterSpacing: 0.5,
  },
  tagline: {
    fontSize: 13,
    color: colors.textMuted,
    marginTop: 6,
    textAlign: 'center',
  },

  card: {
    backgroundColor: colors.card,
    borderRadius: radius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    elevation: 12,
  },
  cardTitle: { fontSize: 22, fontWeight: '700', color: colors.textPrimary, marginBottom: 4 },
  cardSubtitle: { fontSize: 14, color: colors.textSecondary, marginBottom: spacing.lg },
  inputSpacing: { marginBottom: spacing.md },

  loginBtn: { marginTop: spacing.lg },

  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: spacing.lg,
  },
  line: { flex: 1, height: 1, backgroundColor: colors.divider },
  dividerText: {
    color: colors.textMuted,
    fontSize: 12,
    marginHorizontal: spacing.sm,
  },

  registerLink: { alignItems: 'center', paddingVertical: spacing.sm },
  registerLinkText: { fontSize: 14, color: colors.textSecondary },
  registerLinkBold: { color: colors.primary, fontWeight: '700' },

  footer: {
    textAlign: 'center',
    color: colors.textMuted,
    fontSize: 12,
    marginTop: spacing.xl,
    lineHeight: 18,
  },
});
