/**
 * FreeWay Community — VehiclesScreen
 * Manage registered vehicles: list, add, delete.
 */
import React, { useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  Alert, Modal, RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { api } from '../../api/client';
import { Card } from '../../components/Card';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { PlateDisplay } from '../../components/PlateDisplay';
import { EmptyState } from '../../components/EmptyState';
import { colors, spacing, radius } from '../../theme';

const VEHICLE_TYPES = ['CAR', 'MOTORCYCLE', 'TRUCK', 'BUS', 'AUTO', 'OTHER'];
const VEHICLE_EMOJIS = { CAR: '🚗', MOTORCYCLE: '🏍️', TRUCK: '🚛', BUS: '🚌', AUTO: '🛺', OTHER: '🚐' };

function VehicleCard({ vehicle, onDelete }) {
  return (
    <Card style={styles.vehicleCard}>
      <View style={styles.vehicleRow}>
        <Text style={styles.vehicleEmoji}>
          {VEHICLE_EMOJIS[vehicle.vehicle_type || vehicle.vehicleType] || '🚗'}
        </Text>
        <View style={styles.vehicleInfo}>
          <PlateDisplay plate={vehicle.vehicle_number || vehicle.vehicleNumber} size="sm" />
          {vehicle.nickname && (
            <Text style={styles.nickname}>{vehicle.nickname}</Text>
          )}
          <Text style={styles.vehicleType}>{vehicle.vehicle_type || vehicle.vehicleType}</Text>
        </View>
        <TouchableOpacity
          style={styles.deleteBtn}
          onPress={() => onDelete(vehicle)}
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
        >
          <Text style={styles.deleteIcon}>🗑️</Text>
        </TouchableOpacity>
      </View>
    </Card>
  );
}

export default function VehiclesScreen() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ vehicleNumber: '', nickname: '', vehicleType: 'CAR' });
  const [formErrors, setFormErrors] = useState({});
  const [addLoading, setAddLoading] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await api.listVehicles();
      const list = Array.isArray(data) ? data : (data?.vehicles || []); setVehicles(list);
    } catch (err) {
      console.warn('Vehicles load error:', err);
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

  const validateForm = () => {
    const e = {};
    if (!form.vehicleNumber.trim()) e.vehicleNumber = 'Required';
    setFormErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleAdd = async () => {
    if (!validateForm()) return;
    setAddLoading(true);
    try {
      await api.addVehicle(
        form.vehicleNumber.trim().toUpperCase(),
        form.nickname || null,
        form.vehicleType,
      );
      setShowModal(false);
      setForm({ vehicleNumber: '', nickname: '', vehicleType: 'CAR' });
      await load();
    } catch (err) {
      Alert.alert('Error', err.message);
    } finally {
      setAddLoading(false);
    }
  };

  const handleDelete = (vehicle) => {
    Alert.alert(
      'Remove Vehicle?',
      `Remove ${vehicle.vehicle_number} from your account?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove', style: 'destructive', onPress: async () => {
            try {
              await api.deleteVehicle(vehicle.id);
              await load();
            } catch (err) {
              Alert.alert('Error', err.message);
            }
          },
        },
      ],
    );
  };

  return (
    <View style={styles.root}>
      <FlatList
        data={vehicles}
        keyExtractor={(v) => v.id}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
        }
        ListHeaderComponent={
          <Button
            title="+ Add Vehicle"
            onPress={() => setShowModal(true)}
            style={styles.addBtn}
          />
        }
        ListEmptyComponent={
          loading ? (
            <View style={styles.loadingWrap}><Text style={styles.loadingText}>Loading...</Text></View>
          ) : (
            <EmptyState
              emoji="🚗"
              title="No vehicles registered"
              subtitle="Add your vehicle to receive obstruction alerts when someone needs you to move"
            />
          )
        }
        renderItem={({ item }) => (
          <VehicleCard vehicle={item} onDelete={handleDelete} />
        )}
      />

      {/* Add Vehicle Modal */}
      <Modal visible={showModal} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add Vehicle</Text>
              <TouchableOpacity onPress={() => setShowModal(false)}>
                <Text style={styles.modalClose}>✕</Text>
              </TouchableOpacity>
            </View>

            <Input
              label="Vehicle Number"
              value={form.vehicleNumber}
              onChangeText={(v) => setForm((f) => ({ ...f, vehicleNumber: v }))}
              placeholder="MH-12-AB-1234"
              autoCapitalize="characters"
              error={formErrors.vehicleNumber}
            />

            <Input
              label="Nickname (Optional)"
              value={form.nickname}
              onChangeText={(v) => setForm((f) => ({ ...f, nickname: v }))}
              placeholder="My Car, Office Vehicle..."
              autoCapitalize="words"
            />

            {/* Vehicle Type Selector */}
            <Text style={styles.typeLabel}>Vehicle Type</Text>
            <View style={styles.typeGrid}>
              {VEHICLE_TYPES.map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[styles.typeChip, form.vehicleType === type && styles.typeChipActive]}
                  onPress={() => setForm((f) => ({ ...f, vehicleType: type }))}
                >
                  <Text style={styles.typeEmoji}>{VEHICLE_EMOJIS[type]}</Text>
                  <Text style={[styles.typeText, form.vehicleType === type && styles.typeTextActive]}>
                    {type}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.modalActions}>
              <Button title="Cancel" onPress={() => setShowModal(false)} variant="secondary" style={styles.modalBtn} />
              <Button title="Add Vehicle" onPress={handleAdd} loading={addLoading} style={styles.modalBtn} />
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  list: { padding: spacing.lg, paddingBottom: spacing.xxl },
  addBtn: { marginBottom: spacing.lg },

  vehicleCard: { marginBottom: spacing.sm },
  vehicleRow: { flexDirection: 'row', alignItems: 'center' },
  vehicleEmoji: { fontSize: 28, marginRight: spacing.md },
  vehicleInfo: { flex: 1 },
  nickname: { fontSize: 13, color: colors.textSecondary, marginTop: 4 },
  vehicleType: { fontSize: 11, color: colors.textMuted, marginTop: 2, textTransform: 'uppercase' },
  deleteBtn: { padding: 4 },
  deleteIcon: { fontSize: 18 },

  loadingWrap: { alignItems: 'center', padding: spacing.xxl },
  loadingText: { color: colors.textMuted },

  // Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  modalCard: {
    backgroundColor: colors.backgroundSecondary,
    borderTopLeftRadius: radius.xl,
    borderTopRightRadius: radius.xl,
    padding: spacing.lg,
    paddingBottom: spacing.xxl,
    borderTopWidth: 1,
    borderColor: colors.cardBorder,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  modalTitle: { fontSize: 18, fontWeight: '700', color: colors.textPrimary },
  modalClose: { fontSize: 18, color: colors.textMuted, padding: 4 },

  typeLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  typeGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.lg },
  typeChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: radius.md,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    gap: 4,
  },
  typeChipActive: { borderColor: colors.primary, backgroundColor: colors.infoBg },
  typeEmoji: { fontSize: 14 },
  typeText: { fontSize: 12, color: colors.textSecondary, fontWeight: '600' },
  typeTextActive: { color: colors.primary },

  modalActions: { flexDirection: 'row', gap: spacing.sm },
  modalBtn: { flex: 1 },
});
