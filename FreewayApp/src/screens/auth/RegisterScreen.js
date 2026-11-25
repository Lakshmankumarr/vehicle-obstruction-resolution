/**
 * FreeWay Community — RegisterScreen
 * New user registration with vehicle number and password.
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

export default function RegisterScreen({ navigation }) {
  const { register } = useAuth();
  const [form, setForm] = useState({
    name: '',
    vehicleNumber: '',
    phoneNumber: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const set = (key) => (val) => setForm((f) => ({ ...f, [key]: val }));

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = 'Full name is required';
    if (!form.vehicleNumber.trim()) e.vehicleNumber = 'Vehicle number is required';
    if (!/^\d{10}$/.test(form.phoneNumber.replace(/\D/g, '')))
      e.phoneNumber = 'Enter a valid 10-digit phone number';
    if (form.password.length < 8) e.password = 'Password must be at least 8 characters';
    if (form.password !== form.confirmPassword) e.confirmPassword = 'Passwords do not match';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleRegister = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      await register(
        form.vehicleNumber.trim().toUpperCase(),
        form.password,
        form.phoneNumber.replace(/\D/g, ''),
        form.name.trim(),
      );
      Alert.alert(
        'Account Created! 🎉',
        'Your account has been created. Please sign in.',
        [{ text: 'Sign In', onPress: () => { const result = navigation.navigate('Login'); if (result && typeof result.catch === 'function') result.catch(() => {}); } }],
      );
    } catch (err) {
      Alert.alert('Registration Failed', err.message || 'Could not create account.');
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
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>
            Register your vehicle to receive and send obstruction alerts
          </Text>
        </View>

        {/* Form */}
        <View style={styles.card}>
          <Input
            label="Full Name"
            value={form.name}
            onChangeText={set('name')}
            placeholder="Rajesh Kumar"
            autoCapitalize="words"
            error={errors.name}
          />
          <Input
            label="Vehicle Number"
            value={form.vehicleNumber}
            onChangeText={set('vehicleNumber')}
            placeholder="MH-12-AB-1234"
            autoCapitalize="characters"
            error={errors.vehicleNumber}
          />
          <Input
            label="Phone Number"
            value={form.phoneNumber}
            onChangeText={set('phoneNumber')}
            placeholder="9876543210"
            keyboardType="phone-pad"
            error={errors.phoneNumber}
          />
          <Input
            label="Password"
            value={form.password}
            onChangeText={set('password')}
            placeholder="Min. 8 characters"
            secureTextEntry
            error={errors.password}
          />
          <Input
            label="Confirm Password"
            value={form.confirmPassword}
            onChangeText={set('confirmPassword')}
            placeholder="Re-enter password"
            secureTextEntry
            error={errors.confirmPassword}
          />

          {/* Privacy Notice */}
          <View style={styles.privacyBox}>
            <Text style={styles.privacyText}>
              🔒 Your vehicle number is always masked before being shared. Only the last 4
              characters are visible to other users to protect your privacy.
            </Text>
          </View>

          <Button
            title="Create Account"
            onPress={handleRegister}
            loading={loading}
            size="lg"
          />
        </View>

        <TouchableOpacity
          style={styles.loginLink}
          onPress={() => { const result = navigation.navigate('Login'); if (result && typeof result.catch === 'function') result.catch(() => {}); }}
        >
          <Text style={styles.loginText}>
            Already registered?{' '}
            <Text style={styles.loginBold}>Sign In →</Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  scroll: { flexGrow: 1, padding: spacing.lg },

  header: { paddingTop: spacing.xl, paddingBottom: spacing.lg },
  backBtn: { marginBottom: spacing.md },
  backText: { color: colors.primary, fontSize: 15, fontWeight: '600' },
  title: { fontSize: 26, fontWeight: '800', color: colors.textPrimary },
  subtitle: { fontSize: 14, color: colors.textSecondary, marginTop: 6, lineHeight: 20 },

  card: {
    backgroundColor: colors.card,
    borderRadius: radius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 10,
  },

  privacyBox: {
    backgroundColor: colors.infoBg,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  privacyText: { color: colors.info, fontSize: 12, lineHeight: 18 },

  loginLink: { alignItems: 'center', paddingVertical: spacing.lg },
  loginText: { fontSize: 14, color: colors.textSecondary },
  loginBold: { color: colors.primary, fontWeight: '700' },
});
