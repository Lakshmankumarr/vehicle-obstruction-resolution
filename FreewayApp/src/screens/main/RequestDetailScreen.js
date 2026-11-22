/**
 * FreeWay Community — RequestDetailScreen
 * Live view of a single request with action buttons for both parties.
 * Auto-refreshes every 15 seconds while the request is active.
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Alert, RefreshControl, TextInput,
} from 'react-native';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../api/client';
import { Card } from '../../components/Card';
import { Button } from '../../components/Button';
import { StatusBadge } from '../../components/StatusBadge';
import { PlateDisplay } from '../../components/PlateDisplay';
import { colors, spacing, radius } from '../../theme';

const ACTIVE_STATUSES = ['PENDING', 'NOTIFIED', 'ACKNOWLEDGED', 'MOVING'];

export default function RequestDetailScreen({ route, navigation }) {
  const { requestId, request: initialRequest } = route.params;
  const { user } = useAuth();
  const [request, setRequest] = useState(initialRequest);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [responseMsg, setResponseMsg] = useState('');
  const [etaMinutes, setEtaMinutes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const pollRef = useRef(null);

  const load = useCallback(async () => {
    try {
      const data = await api.getRequestStatus(requestId);
      setRequest(data);
      return data;
    } catch (err) {
      console.warn('Load request error:', err);
    }
  }, [requestId]);

  useEffect(() => {
    setLoading(true);
    load().finally(() => setLoading(false));
  }, [load]);

  // Auto-poll while active
  useEffect(() => {
    if (request && ACTIVE_STATUSES.includes(request.status)) {
      pollRef.current = setInterval(load, 15000);
    }
    return () => clearInterval(pollRef.current);
  }, [request?.status, load]);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const isRequester = (user?.id === (request?.requesterId || request?.requester_id)) || Boolean(request?.isRequester);
  const isBlocked = ACTIVE_STATUSES.includes(request?.status);

  // --- Actions ---
  const handleRespond = async (response) => {
    setActionLoading(true);
    try {
      await api.respondRequest(
        requestId,
        response,
        responseMsg || null,
        etaMinutes ? parseInt(etaMinutes) : null,
      );
      await load();
    } catch (err) {
      Alert.alert('Error', err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = () => {
    Alert.alert('Mark as Resolved?', 'Confirm that the vehicle has moved.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Resolved ✅', onPress: async () => {
          setActionLoading(true);
          try { await api.resolveRequest(requestId); await load(); }
          catch (err) { Alert.alert('Error', err.message); }
          finally { setActionLoading(false); }
        },
      },
    ]);
  };

  const handleCancel = () => {
    Alert.alert('Cancel Request?', 'This will cancel your notification.', [
      { text: 'Keep', style: 'cancel' },
      {
        text: 'Cancel Request', style: 'destructive', onPress: async () => {
          setActionLoading(true);
          try { await api.cancelRequest(requestId); await load(); }
          catch (err) { Alert.alert('Error', err.message); }
          finally { setActionLoading(false); }
        },
      },
    ]);
  };

  const handleReport = () =>
    navigation.navigate('ReportUser', { targetUserId: (request.targetUserId || request.target_user_id), requestId });

  if (!request) {
    return (
      <View style={styles.center}>
        <Text style={styles.loadingText}>{loading ? 'Loading...' : 'Request not found.'}</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
    >
      {/* Back */}
      <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backWrap}>
        <Text style={styles.back}>← Back</Text>
      </TouchableOpacity>

      {/* Status Hero */}
      <Card style={[styles.heroCard, request.is_emergency && styles.heroEmergency]}>
        <View style={styles.heroTop}>
          <Text style={styles.heroEmoji}>
            {request.is_emergency ? '⚡' : '🚗'}
          </Text>
          <StatusBadge status={request.is_emergency ? 'EMERGENCY' : request.status} />
        </View>
        <Text style={styles.heroTitle}>
          {isRequester ? 'Your Request' : 'Incoming Alert'}
        </Text>

        <View style={styles.plateRow}>
          <View style={styles.plateBlock}>
            <Text style={styles.plateLabel}>
              {isRequester ? 'Blocking Vehicle' : 'Requester'}
            </Text>
            <PlateDisplay
              plate={isRequester ? (request.maskedTargetVehicle || request.target_vehicle) : (request.requester_vehicle || request.maskedTargetVehicle || 'Vehicle')}
              size="md"
            />
          </View>
        </View>

        {request.message && (
          <View style={styles.msgBox}>
            <Text style={styles.msgText}>"{request.message}"</Text>
          </View>
        )}

        <Text style={styles.timestamp}>
          Sent {request.formattedCreatedIST || (request.createdAt || request.created_at ? new Date(request.createdAt || request.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) : '')}
        </Text>
      </Card>

      {/* Response Info */}
      {request.response && (
        <Card style={styles.responseCard}>
          <Text style={styles.responseTitle}>Response</Text>
          <Text style={styles.responseValue}>{request.response}</Text>
          {(request.responseMessage || request.response_message) && (
            <Text style={styles.responseMsg}>"{(request.responseMessage || request.response_message)}"</Text>
          )}
          {(request.etaMinutes || request.eta_minutes) && (
            <Text style={styles.eta}>ETA: {(request.etaMinutes || request.eta_minutes)} minutes</Text>
          )}
        </Card>
      )}

      {/* Actions for the RECEIVER (blocked vehicle owner) */}
      {!isRequester && isBlocked && (
        <Card style={styles.actionCard}>
          <Text style={styles.actionTitle}>Your Response</Text>
          <TextInput
            style={styles.responseInput}
            value={responseMsg}
            onChangeText={setResponseMsg}
            placeholder="Optional message..."
            placeholderTextColor={colors.textMuted}
            multiline
          />
          <TextInput
            style={[styles.responseInput, { marginTop: spacing.sm }]}
            value={etaMinutes}
            onChangeText={setEtaMinutes}
            placeholder="ETA in minutes (optional)"
            placeholderTextColor={colors.textMuted}
            keyboardType="number-pad"
          />

          <View style={styles.buttonRow}>
            <Button
              title="✅ Acknowledged"
              onPress={() => handleRespond('ACKNOWLEDGED')}
              variant="secondary"
              loading={actionLoading}
              style={styles.halfBtn}
              fullWidth={false}
            />
            <Button
              title="🚗 I'm Moving"
              onPress={() => handleRespond('MOVING')}
              variant="primary"
              loading={actionLoading}
              style={styles.halfBtn}
              fullWidth={false}
            />
          </View>

          <Button
            title="🚫 Cannot Move Right Now"
            onPress={() => handleRespond('CANNOT_MOVE')}
            variant="ghost"
            loading={actionLoading}
            style={{ marginTop: spacing.sm }}
          />
        </Card>
      )}

      {/* Actions for the REQUESTER */}
      {isRequester && isBlocked && (
        <Card style={styles.actionCard}>
          <Text style={styles.actionTitle}>Manage Request</Text>
          <Button
            title="✅ Mark as Resolved"
            onPress={handleResolve}
            loading={actionLoading}
            style={{ marginBottom: spacing.sm }}
          />
          <Button
            title="❌ Cancel Request"
            onPress={handleCancel}
            variant="danger"
            loading={actionLoading}
          />
        </Card>
      )}

      {/* Report */}
      {isRequester && (
        <TouchableOpacity style={styles.reportLink} onPress={handleReport}>
          <Text style={styles.reportText}>🚩 Report Abuse / Misconduct</Text>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.background },
  loadingText: { color: colors.textMuted },

  backWrap: { marginBottom: spacing.md },
  back: { color: colors.primary, fontSize: 15, fontWeight: '600' },

  heroCard: { marginBottom: spacing.md },
  heroEmergency: { borderColor: colors.danger, borderWidth: 1.5 },
  heroTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.sm },
  heroEmoji: { fontSize: 32 },
  heroTitle: { fontSize: 20, fontWeight: '800', color: colors.textPrimary, marginBottom: spacing.md },
  plateRow: { marginBottom: spacing.md },
  plateBlock: {},
  plateLabel: { fontSize: 11, color: colors.textMuted, fontWeight: '600', textTransform: 'uppercase', marginBottom: 6 },
  msgBox: { backgroundColor: colors.backgroundSecondary, borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.sm },
  msgText: { color: colors.textSecondary, fontSize: 14, fontStyle: 'italic', lineHeight: 20 },
  timestamp: { fontSize: 11, color: colors.textMuted, marginTop: 4 },

  responseCard: { marginBottom: spacing.md, borderColor: colors.successBg },
  responseTitle: { fontSize: 13, fontWeight: '700', color: colors.textSecondary, textTransform: 'uppercase', marginBottom: 6 },
  responseValue: { fontSize: 16, fontWeight: '700', color: colors.success },
  responseMsg: { fontSize: 13, color: colors.textMuted, marginTop: 4, fontStyle: 'italic' },
  eta: { fontSize: 13, color: colors.warning, marginTop: 4 },

  actionCard: { marginBottom: spacing.md },
  actionTitle: { fontSize: 15, fontWeight: '700', color: colors.textPrimary, marginBottom: spacing.md },
  responseInput: {
    backgroundColor: colors.inputBg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.inputBorder,
    color: colors.textPrimary,
    padding: spacing.md,
    fontSize: 14,
    minHeight: 48,
  },
  buttonRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: spacing.md, gap: spacing.sm },
  halfBtn: { flex: 1 },

  reportLink: { alignItems: 'center', paddingVertical: spacing.md },
  reportText: { color: colors.danger, fontSize: 13, fontWeight: '600' },
});
