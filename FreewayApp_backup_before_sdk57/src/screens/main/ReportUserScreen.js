/**
 * FreeWay Community — ReportUserScreen
 * Submit an abuse/misconduct report against another user.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert,
} from 'react-native';
import { api } from '../../api/client';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { colors, spacing, radius } from '../../theme';

const REASONS = [
  { key: 'SPAM', label: '🚫 Spam / Fake Requests', desc: 'Sending repeated or false obstruction alerts' },
  { key: 'HARASSMENT', label: '😠 Harassment', desc: 'Abusive or threatening messages' },
  { key: 'IMPERSONATION', label: '🎭 Impersonation', desc: 'Pretending to be someone else' },
  { key: 'ABUSE', label: '⚠️ Platform Abuse', desc: 'Misusing FreeWay for non-obstruction purposes' },
  { key: 'OTHER', label: '📋 Other', desc: 'Other policy violations' },
];

export default function ReportUserScreen({ route, navigation }) {
  const { targetUserId, requestId } = route.params || {};
  const [selectedReason, setSelectedReason] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selectedReason) {
      Alert.alert('Select a Reason', 'Please select a reason for your report.');
      return;
    }
    setLoading(true);
    try {
      await api.submitReport(targetUserId, selectedReason, description || null, requestId || null);
      Alert.alert(
        'Report Submitted ✅',
        'Thank you. Our moderation team will review this within 24 hours.',
        [{ text: 'OK', onPress: () => navigation.goBack() }],
      );
    } catch (err) {
      Alert.alert('Error', err.message || 'Could not submit report.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backWrap}>
        <Text style={styles.back}>← Back</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Report Abuse</Text>
      <Text style={styles.subtitle}>
        Help keep FreeWay safe. Reports are anonymous and reviewed by our moderation team.
      </Text>

      <Text style={styles.sectionLabel}>Select Reason</Text>
      {REASONS.map((r) => (
        <TouchableOpacity
          key={r.key}
          style={[styles.reasonCard, selectedReason === r.key && styles.reasonCardActive]}
          onPress={() => setSelectedReason(r.key)}
          activeOpacity={0.8}
        >
          <View style={styles.reasonRow}>
            <View style={[styles.radioOuter, selectedReason === r.key && styles.radioActive]}>
              {selectedReason === r.key && <View style={styles.radioInner} />}
            </View>
            <View style={styles.reasonText}>
              <Text style={styles.reasonLabel}>{r.label}</Text>
              <Text style={styles.reasonDesc}>{r.desc}</Text>
            </View>
          </View>
        </TouchableOpacity>
      ))}

      <Input
        label="Additional Details (Optional)"
        value={description}
        onChangeText={setDescription}
        placeholder="Describe what happened..."
        autoCapitalize="sentences"
        style={styles.descInput}
      />

      <View style={styles.notice}>
        <Text style={styles.noticeText}>
          🔒 Reports are confidential. False reports may result in account suspension.
        </Text>
      </View>

      <Button
        title="Submit Report"
        onPress={handleSubmit}
        loading={loading}
        variant="danger"
        size="lg"
        disabled={!selectedReason}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },

  backWrap: { marginBottom: spacing.md },
  back: { color: colors.primary, fontSize: 15, fontWeight: '600' },
  title: { fontSize: 26, fontWeight: '800', color: colors.textPrimary },
  subtitle: { fontSize: 14, color: colors.textSecondary, marginTop: 6, lineHeight: 20, marginBottom: spacing.lg },

  sectionLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.textMuted,
    textTransform: 'uppercase',
    marginBottom: spacing.sm,
  },

  reasonCard: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    padding: spacing.md,
    borderWidth: 1.5,
    borderColor: colors.cardBorder,
    marginBottom: spacing.sm,
  },
  reasonCardActive: { borderColor: colors.danger, backgroundColor: colors.dangerBg },
  reasonRow: { flexDirection: 'row', alignItems: 'center' },
  radioOuter: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: colors.textMuted,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  radioActive: { borderColor: colors.danger },
  radioInner: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.danger },
  reasonText: { flex: 1 },
  reasonLabel: { fontSize: 14, fontWeight: '700', color: colors.textPrimary },
  reasonDesc: { fontSize: 12, color: colors.textSecondary, marginTop: 2 },

  descInput: { marginTop: spacing.md },

  notice: {
    backgroundColor: colors.warningBg,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  noticeText: { fontSize: 12, color: colors.warning, lineHeight: 18 },
});
