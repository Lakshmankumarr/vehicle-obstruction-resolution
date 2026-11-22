/**
 * FreeWay Community — NewRequestScreen
 * Send an obstruction notification by plate number or ALPR camera scan.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, KeyboardAvoidingView,
  Platform, TouchableOpacity, Switch, Alert,
} from 'react-native';
import { api } from '../../api/client';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Card } from '../../components/Card';
import { PlateDisplay } from '../../components/PlateDisplay';
import { colors, spacing, radius } from '../../theme';

const PRESET_MESSAGES = [
  'Please move your vehicle, you are blocking my exit.',
  'Your vehicle is blocking a fire lane. Please move immediately.',
  'You are double-parked and blocking traffic. Kindly move.',
  'Emergency access needed. Please relocate your vehicle.',
];

export default function NewRequestScreen({ navigation }) {
  const [targetPlate, setTargetPlate] = useState('');
  const [message, setMessage] = useState('');
  const [isEmergency, setIsEmergency] = useState(false);
  const [loading, setLoading] = useState(false);
  const [identifyLoading, setIdentifyLoading] = useState(false);
  const [identified, setIdentified] = useState(null);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const e = {};
    if (!targetPlate.trim()) e.targetPlate = 'Vehicle number is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleIdentify = async () => {
    if (!targetPlate.trim()) {
      setErrors({ targetPlate: 'Enter a plate number first' });
      return;
    }
    setIdentifyLoading(true);
    setIdentified(null);
    try {
      const data = await api.identifyVehicle(targetPlate.trim().toUpperCase());
      setIdentified(data);
    } catch (err) {
      Alert.alert('Not Found', err.message || 'Vehicle not registered on FreeWay.');
    } finally {
      setIdentifyLoading(false);
    }
  };

  const handleSend = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      const data = await api.createRequest(
        targetPlate.trim().toUpperCase(),
        message || null,
        isEmergency,
      );
      Alert.alert(
        isEmergency ? '⚡ Emergency Sent!' : '✅ Notification Sent!',
        'The vehicle owner has been anonymously notified. You will be updated when they respond.',
        [{ text: 'Track Status', onPress: () => navigation.replace('RequestDetail', { requestId: data.id, request: data }) }],
      );
    } catch (err) {
      Alert.alert('Failed to Send', err.message || 'Could not send notification.');
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
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Text style={styles.back}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Send Alert</Text>
          <Text style={styles.subtitle}>
            Notify the registered owner of the blocking vehicle anonymously
          </Text>
        </View>

        {/* Vehicle Number */}
        <Card style={styles.card}>
          <Text style={styles.sectionTitle}>🚗 Blocking Vehicle</Text>
          <Input
            label="Vehicle Number"
            value={targetPlate}
            onChangeText={(t) => { setTargetPlate(t); setIdentified(null); }}
            placeholder="MH-12-AB-1234"
            autoCapitalize="characters"
            error={errors.targetPlate}
          />

          {identified && (
            <View style={styles.identifiedBox}>
              <Text style={styles.identifiedLabel}>✅ Vehicle found on FreeWay</Text>
              <PlateDisplay plate={identified.masked_number} size="md" style={styles.identifiedPlate} />
            </View>
          )}

          <Button
            title={identifyLoading ? 'Checking...' : '🔍 Verify Vehicle'}
            onPress={handleIdentify}
            variant="outline"
            size="sm"
            loading={identifyLoading}
            style={styles.verifyBtn}
          />
        </Card>

        {/* Message */}
        <Card style={styles.card}>
          <Text style={styles.sectionTitle}>💬 Message (Optional)</Text>
          <Text style={styles.sectionSub}>
            Choose a preset or write a custom message
          </Text>

          {/* Preset pills */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.presetScroll}>
            {PRESET_MESSAGES.map((p, i) => (
              <TouchableOpacity
                key={i}
                style={[styles.preset, message === p && styles.presetActive]}
                onPress={() => setMessage(message === p ? '' : p)}
              >
                <Text style={[styles.presetText, message === p && styles.presetTextActive]} numberOfLines={2}>
                  {p}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          <Input
            label="Custom Message"
            value={message}
            onChangeText={setMessage}
            placeholder="Or type your own message..."
            autoCapitalize="sentences"
            style={styles.customInput}
          />
        </Card>

        {/* Emergency Toggle */}
        <Card style={[styles.card, isEmergency && styles.cardEmergency]}>
          <View style={styles.toggleRow}>
            <View style={styles.toggleInfo}>
              <Text style={styles.toggleTitle}>⚡ Emergency Mode</Text>
              <Text style={styles.toggleSub}>
                Escalates priority and sends urgent alerts. Use only for genuine emergencies.
              </Text>
            </View>
            <Switch
              value={isEmergency}
              onValueChange={setIsEmergency}
              trackColor={{ false: colors.inputBorder, true: colors.danger }}
              thumbColor={isEmergency ? '#fff' : colors.textMuted}
            />
          </View>
        </Card>

        {/* Privacy Notice */}
        <View style={styles.privacyBox}>
          <Text style={styles.privacyText}>
            🔒 Your identity is protected. The vehicle owner will only see a masked version
            of your vehicle number. No personal data is shared.
          </Text>
        </View>

        {/* Send */}
        <Button
          title={isEmergency ? '⚡ Send Emergency Alert' : '📨 Send Notification'}
          onPress={handleSend}
          loading={loading}
          variant={isEmergency ? 'danger' : 'primary'}
          size="lg"
        />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: spacing.lg, paddingBottom: spacing.xxl },

  header: { paddingTop: spacing.sm, paddingBottom: spacing.lg },
  back: { color: colors.primary, fontSize: 15, fontWeight: '600', marginBottom: spacing.md },
  title: { fontSize: 26, fontWeight: '800', color: colors.textPrimary },
  subtitle: { fontSize: 13, color: colors.textSecondary, marginTop: 6, lineHeight: 20 },

  card: { marginBottom: spacing.md },
  cardEmergency: { borderColor: colors.danger, borderWidth: 1.5 },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: colors.textPrimary, marginBottom: 12 },
  sectionSub: { fontSize: 12, color: colors.textMuted, marginBottom: 12 },

  identifiedBox: {
    backgroundColor: colors.successBg,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  identifiedLabel: { fontSize: 12, color: colors.success, fontWeight: '700', marginBottom: 8 },
  identifiedPlate: {},

  verifyBtn: { marginTop: spacing.sm },

  presetScroll: { marginBottom: spacing.md },
  preset: {
    backgroundColor: colors.inputBg,
    borderRadius: radius.md,
    padding: spacing.sm,
    marginRight: spacing.sm,
    maxWidth: 200,
    borderWidth: 1,
    borderColor: colors.inputBorder,
  },
  presetActive: { borderColor: colors.primary, backgroundColor: colors.infoBg },
  presetText: { fontSize: 12, color: colors.textSecondary, lineHeight: 16 },
  presetTextActive: { color: colors.info },
  customInput: { marginTop: spacing.sm, marginBottom: 0 },

  toggleRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  toggleInfo: { flex: 1, marginRight: spacing.md },
  toggleTitle: { fontSize: 15, fontWeight: '700', color: colors.textPrimary },
  toggleSub: { fontSize: 12, color: colors.textSecondary, marginTop: 4, lineHeight: 18 },

  privacyBox: {
    backgroundColor: colors.infoBg,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  privacyText: { fontSize: 12, color: colors.info, lineHeight: 18 },
});
