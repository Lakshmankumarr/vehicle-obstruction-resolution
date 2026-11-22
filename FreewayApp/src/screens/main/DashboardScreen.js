/**
 * FreeWay Community — DashboardScreen
 * Main home screen showing active requests, quick actions, and user info.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, RefreshControl,
  TouchableOpacity, Alert,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../api/client';
import { Card } from '../../components/Card';
import { Button } from '../../components/Button';
import { StatusBadge } from '../../components/StatusBadge';
import { PlateDisplay } from '../../components/PlateDisplay';
import { EmptyState } from '../../components/EmptyState';
import { colors, spacing, radius } from '../../theme';

function RequestCard({ req, onPress }) {
  const isIncoming = req.direction === 'incoming' || req.isTarget;
  const plateText =
    req.maskedTargetVehicle ||
    req.target_vehicle ||
    req.masked_target_vehicle ||
    req.targetVehicle ||
    req.requester_vehicle ||
    'Vehicle';
  const dateVal = req.createdAt || req.created_at;
  const timeText = req.formattedCreatedIST || (dateVal ? new Date(dateVal).toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    dateStyle: 'medium',
    timeStyle: 'short',
  }) : '');

  return (
    <TouchableOpacity onPress={() => onPress(req)} activeOpacity={0.85}>
      <Card style={styles.reqCard}>
        <View style={styles.reqHeader}>
          <View style={styles.reqDirection}>
            <Text style={styles.reqDirectionIcon}>{isIncoming ? '📨' : '📤'}</Text>
            <Text style={styles.reqDirectionText}>
              {isIncoming ? 'Incoming' : 'Outgoing'}
            </Text>
          </View>
          <StatusBadge status={req.is_emergency ? 'EMERGENCY' : req.status} />
        </View>

        <PlateDisplay
          plate={plateText}
          size="sm"
          style={styles.plate}
        />

        {req.message && (
          <Text style={styles.reqMessage} numberOfLines={2}>
            "{req.message}"
          </Text>
        )}

        {timeText ? <Text style={styles.reqTime}>{timeText}</Text> : null}
      </Card>
    </TouchableOpacity>
  );
}

export default function DashboardScreen({ navigation }) {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await api.getHistory();
      let allRequests = [];
      if (Array.isArray(data.requests)) {
        allRequests = data.requests;
      } else if (Array.isArray(data.sent) || Array.isArray(data.received)) {
        const sent = (data.sent || []).map((r) => ({ ...r, direction: 'outgoing' }));
        const received = (data.received || []).map((r) => ({ ...r, direction: 'incoming' }));
        allRequests = [...received, ...sent].sort(
          (a, b) => new Date(b.createdAt || b.created_at || 0) - new Date(a.createdAt || a.created_at || 0)
        );
      }
      setHistory(allRequests);
    } catch (err) {
      console.warn('Dashboard load error:', err);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      load().finally(() => setLoading(false));
    }, [load]),
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  // Active requests = not resolved/cancelled/expired
  const active = history.filter(
    (r) => !['RESOLVED', 'CANCELLED', 'EXPIRED'].includes(r.status),
  );
  const recent = history.slice(0, 5);

  const openRequest = (req) =>
    navigation.navigate('RequestDetail', { requestId: req.id, request: req });

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
    >
      {/* Greeting */}
      <View style={styles.greeting}>
        <View>
          <Text style={styles.greetingHello}>
            Hello, {user?.name || 'Driver'} 👋
          </Text>
          <Text style={styles.greetingSubtext}>Stay connected on the road</Text>
        </View>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {(user?.name || 'U')[0].toUpperCase()}
          </Text>
        </View>
      </View>

      {/* Quick Action */}
      <Card style={styles.quickCard}>
        <Text style={styles.quickTitle}>Someone blocking your way?</Text>
        <Text style={styles.quickSub}>Send an anonymous notification in seconds</Text>
        <Button
          title="🚨  Request to Move"
          onPress={() => navigation.navigate('NewRequest')}
          size="lg"
          style={styles.quickBtn}
        />
      </Card>

      {/* Active Requests */}
      {active.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Active Requests</Text>
          {active.map((r) => (
            <RequestCard key={r.id} req={r} onPress={openRequest} />
          ))}
        </View>
      )}

      {/* Recent History */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          <TouchableOpacity onPress={() => navigation.navigate('History')}>
            <Text style={styles.seeAll}>See all →</Text>
          </TouchableOpacity>
        </View>

        {loading && !refreshing ? (
          <View style={styles.loadingWrap}>
            <Text style={styles.loadingText}>Loading...</Text>
          </View>
        ) : recent.length === 0 ? (
          <EmptyState
            emoji="📭"
            title="No activity yet"
            subtitle="Your request history will appear here"
          />
        ) : (
          recent.map((r) => <RequestCard key={r.id} req={r} onPress={openRequest} />)
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },

  greeting: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
    paddingTop: spacing.sm,
  },
  greetingHello: { fontSize: 22, fontWeight: '800', color: colors.textPrimary },
  greetingSubtext: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { fontSize: 18, fontWeight: '700', color: '#fff' },

  quickCard: {
    marginBottom: spacing.lg,
    borderColor: colors.primary + '44',
    borderWidth: 1,
  },
  quickTitle: { fontSize: 17, fontWeight: '700', color: colors.textPrimary },
  quickSub: { fontSize: 13, color: colors.textSecondary, marginTop: 4, marginBottom: spacing.md },
  quickBtn: {},

  section: { marginBottom: spacing.lg },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: colors.textPrimary },
  seeAll: { fontSize: 13, color: colors.primary, fontWeight: '600' },

  reqCard: { marginBottom: spacing.sm },
  reqHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.sm },
  reqDirection: { flexDirection: 'row', alignItems: 'center' },
  reqDirectionIcon: { fontSize: 14, marginRight: 4 },
  reqDirectionText: { fontSize: 12, color: colors.textSecondary, fontWeight: '600' },
  plate: { marginBottom: spacing.sm },
  reqMessage: { fontSize: 13, color: colors.textMuted, fontStyle: 'italic', marginBottom: 6 },
  reqTime: { fontSize: 11, color: colors.textMuted },

  loadingWrap: { alignItems: 'center', padding: spacing.xl },
  loadingText: { color: colors.textMuted, fontSize: 14 },
});
