/**
 * FreeWay Community — HistoryScreen
 * Paginated, filterable request history for the current user.
 */
import React, { useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity, RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { api } from '../../api/client';
import { Card } from '../../components/Card';
import { StatusBadge } from '../../components/StatusBadge';
import { PlateDisplay } from '../../components/PlateDisplay';
import { EmptyState } from '../../components/EmptyState';
import { colors, spacing, radius } from '../../theme';

const FILTERS = ['ALL', 'PENDING', 'RESOLVED', 'CANCELLED', 'EMERGENCY'];

export default function HistoryScreen({ navigation }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('ALL');

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
      console.warn('History load error:', err);
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

  const filtered = history.filter((r) => {
    if (filter === 'ALL') return true;
    if (filter === 'EMERGENCY') return r.is_emergency;
    return r.status === filter;
  });

  const renderItem = ({ item: r }) => (
    <TouchableOpacity
      onPress={() => navigation.navigate('RequestDetail', { requestId: r.id, request: r })}
      activeOpacity={0.85}
    >
      <Card style={styles.card}>
        <View style={styles.cardTop}>
          <View style={styles.directionBadge}>
            <Text style={styles.directionText}>
              {r.direction === 'incoming' ? '📨 Incoming' : '📤 Outgoing'}
            </Text>
          </View>
          <StatusBadge status={r.is_emergency ? 'EMERGENCY' : r.status} />
        </View>

        <PlateDisplay
          plate={r.maskedTargetVehicle || r.target_vehicle || r.requester_vehicle || 'Vehicle'}
          size="sm"
          style={styles.plate}
        />

        {r.message && (
          <Text style={styles.msg} numberOfLines={1}>
            "{r.message}"
          </Text>
        )}

        <Text style={styles.time}>
          {r.formattedCreatedIST || (r.createdAt || r.created_at ? new Date(r.createdAt || r.created_at).toLocaleString('en-IN', {
            timeZone: 'Asia/Kolkata',
            dateStyle: 'medium',
            timeStyle: 'short',
          }) : '')}
        </Text>
      </Card>
    </TouchableOpacity>
  );

  return (
    <View style={styles.root}>
      {/* Filter Bar */}
      <View style={styles.filterBar}>
        <FlatList
          horizontal
          data={FILTERS}
          keyExtractor={(f) => f}
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterContent}
          renderItem={({ item: f }) => (
            <TouchableOpacity
              style={[styles.filterChip, filter === f && styles.filterChipActive]}
              onPress={() => setFilter(f)}
            >
              <Text style={[styles.filterText, filter === f && styles.filterTextActive]}>
                {f === 'EMERGENCY' ? '⚡ ' : ''}{f}
              </Text>
            </TouchableOpacity>
          )}
        />
      </View>

      {/* Count */}
      <Text style={styles.count}>
        {filtered.length} {filter === 'ALL' ? 'total' : filter.toLowerCase()} request{filtered.length !== 1 ? 's' : ''}
      </Text>

      {/* List */}
      <FlatList
        data={filtered}
        keyExtractor={(r) => r.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
        }
        ListEmptyComponent={
          loading ? (
            <View style={styles.loadingWrap}>
              <Text style={styles.loadingText}>Loading history...</Text>
            </View>
          ) : (
            <EmptyState
              emoji="📋"
              title="No requests found"
              subtitle="Your obstruction request history will appear here"
            />
          )
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },

  filterBar: { borderBottomWidth: 1, borderBottomColor: colors.divider },
  filterContent: { padding: spacing.sm, gap: spacing.sm, flexDirection: 'row' },
  filterChip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: radius.full,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.cardBorder,
  },
  filterChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  filterText: { fontSize: 12, color: colors.textSecondary, fontWeight: '600' },
  filterTextActive: { color: '#fff' },

  count: {
    fontSize: 12,
    color: colors.textMuted,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },

  listContent: { padding: spacing.lg, paddingTop: spacing.sm, paddingBottom: spacing.xxl },
  card: { marginBottom: spacing.sm },
  cardTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.sm },
  directionBadge: {},
  directionText: { fontSize: 12, color: colors.textSecondary, fontWeight: '600' },
  plate: { marginBottom: spacing.sm },
  msg: { fontSize: 12, color: colors.textMuted, fontStyle: 'italic', marginBottom: 4 },
  time: { fontSize: 11, color: colors.textMuted },

  loadingWrap: { alignItems: 'center', padding: spacing.xxl },
  loadingText: { color: colors.textMuted },
});
