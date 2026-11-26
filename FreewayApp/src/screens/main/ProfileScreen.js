/**
 * FreeWay Community — ProfileScreen
 * User profile, account info, privacy settings, and logout.
 */
import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, Switch,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../api/client';
import { Card } from '../../components/Card';
import { Button } from '../../components/Button';
import { colors, spacing, radius } from '../../theme';

const DEVICE_TOKEN_KEY = '@freeway:device_token';

function SettingRow({ icon, title, subtitle, onPress, rightElement, style }) {
  const Inner = (
    <View style={[styles.settingRow, style]}>
      <Text style={styles.settingIcon}>{icon}</Text>
      <View style={styles.settingText}>
        <Text style={styles.settingTitle}>{title}</Text>
        {subtitle && <Text style={styles.settingSub}>{subtitle}</Text>}
      </View>
      {rightElement || <Text style={styles.chevron}>›</Text>}
    </View>
  );
  if (onPress) return <TouchableOpacity onPress={onPress} activeOpacity={0.7}>{Inner}</TouchableOpacity>;
  return Inner;
}

export default function ProfileScreen({ navigation }) {
  const { user, logout } = useAuth();
  const [notifications, setNotifications] = useState(true);
  const [emergencyAlerts, setEmergencyAlerts] = useState(true);

  const handleToggleNotifications = async (value) => {
    setNotifications(value);
    try {
      const token = await AsyncStorage.getItem(DEVICE_TOKEN_KEY);
      if (!token) {
        console.warn('No device token stored locally.');
        return;
      }
      await api.toggleDeviceToken(token, value);
    } catch (e) {
      console.warn('Failed to toggle push notifications:', e);
    }
  };

  const handleLogout = () => {
    Alert.alert('Sign Out?', 'You will need to sign in again.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: logout },
    ]);
  };

  const handleExportData = async () => {
    Alert.alert('Export Data', 'Preparing your data export...', [{ text: 'OK' }]);
    try {
      const data = await api.exportUserData();
      Alert.alert(
        'Export Ready',
        'Your data has been exported. In a production app, this would be saved as a JSON file.',
        [{ text: 'OK' }]
      );
      console.log('GDPR Export:', JSON.stringify(data, null, 2));
    } catch (err) {
      Alert.alert('Export Failed', err.message || 'Could not export data.');
    }
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      '⚠️ Delete Account Permanently?',
      'This will permanently delete your account and ALL associated data:\n\n• Your vehicles\n• Request history (sent & received)\n• Reports made & received\n• Device tokens\n• Audit logs (anonymized)\n\nThis action CANNOT be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete Forever',
          style: 'destructive',
          onPress: async () => {
            Alert.alert(
              'FINAL CONFIRMATION',
              'Type "DELETE" to confirm permanent account deletion.',
              [
                { text: 'Cancel', style: 'cancel' },
                {
                  text: 'I Understand',
                  onPress: async () => {
                    try {
                      await api.deleteAccount();
                      Alert.alert('Account Deleted', 'Your account has been permanently deleted.', [
                        { text: 'OK', onPress: logout }
                      ]);
                    } catch (err) {
                      Alert.alert('Deletion Failed', err.message || 'Could not delete account.');
                    }
                  },
                },
              ]
            );
          },
        },
      ]
    );
  };

  const handleViewPrivacyPolicy = async () => {
    try {
      const data = await api.getPrivacyPolicy();
      const policy = data.policy;
      Alert.alert(
        'Privacy Policy v' + data.version,
        `Data Controller: ${policy.data_controller}\n\n` +
        `Data Collected:\n${policy.data_collected.join(', ')}\n\n` +
        `Purposes:\n${policy.purposes.join(', ')}\n\n` +
        `Retention: ${policy.retention.account_data}\n\n` +
        `Your Rights:\n${policy.user_rights.join('\n')}\n\n` +
        `Contact: ${policy.dpo_contact}`,
        [{ text: 'Close' }]
      );
    } catch (err) {
      Alert.alert('Error', 'Could not load privacy policy.');
    }
  };

  const memberSince = (user?.created_at || user?.createdAt)
    ? new Date(user.created_at || user.createdAt).toLocaleDateString('en-IN', {
        month: 'long', year: 'numeric', timeZone: 'Asia/Kolkata',
      })
    : 'Recently';

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* Profile Header */}
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{(user?.name || 'U')[0].toUpperCase()}</Text>
          <View style={styles.avatarBadge} />
        </View>
        <Text style={styles.name}>{user?.name || 'Driver'}</Text>
        <Text style={styles.vehicleNum}>{user?.vehicle_number || user?.primaryVehicle || '—'}</Text>
        <Text style={styles.since}>Member since {memberSince}</Text>
      </View>

      {/* Stats Row */}
      <View style={styles.statsRow}>
        <View style={styles.statBox}>
          <Text style={styles.statNum}>{user?.total_requests ?? '—'}</Text>
          <Text style={styles.statLabel}>Requests</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statBox}>
          <Text style={styles.statNum}>{user?.resolved_requests ?? '—'}</Text>
          <Text style={styles.statLabel}>Resolved</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statBox}>
          <Text style={[styles.statNum, { color: (user?.reputation_score !== undefined ? user.reputation_score : user?.reputationScore) >= 4 ? colors.success : colors.warning }]}>
            {(user?.reputation_score !== undefined ? user.reputation_score : user?.reputationScore)?.toFixed(1) ?? '—'}
          </Text>
          <Text style={styles.statLabel}>Rep Score</Text>
        </View>
      </View>

      {/* Account */}
      <Text style={styles.sectionTitle}>Account</Text>
      <Card style={styles.card} noPadding>
        <SettingRow
          icon="🚗"
          title="My Vehicles"
          subtitle="Add or manage your registered vehicles"
          onPress={() => navigation.navigate('Vehicles')}
          style={styles.cardRow}
        />
        <View style={styles.divider} />
        <SettingRow
          icon="📱"
          title="Phone Number"
          subtitle={(user?.phoneNumber || user?.phone_number) ? `+91 ${user?.phoneNumber || user?.phone_number}` : 'Not set'}
          style={styles.cardRow}
        />
        <View style={styles.divider} />
        <SettingRow
          icon="🔒"
          title="Change Password"
          subtitle="Update your account password"
          onPress={() => Alert.alert('Coming Soon', 'Password change will be available in the next update.')}
          style={styles.cardRow}
        />
      </Card>

      {/* Notifications */}
      <Text style={styles.sectionTitle}>Notifications</Text>
      <Card style={styles.card} noPadding>
        <SettingRow
          icon="🔔"
          title="Push Notifications"
          subtitle="Alerts when someone needs you to move"
          rightElement={
            <Switch
              value={notifications}
              onValueChange={handleToggleNotifications}
              trackColor={{ false: colors.inputBorder, true: colors.primary }}
              thumbColor="#fff"
            />
          }
          style={styles.cardRow}
        />
        <View style={styles.divider} />
        <SettingRow
          icon="⚡"
          title="Emergency Alerts"
          subtitle="High-priority alerts bypass silent mode"
          rightElement={
            <Switch
              value={emergencyAlerts}
              onValueChange={setEmergencyAlerts}
              trackColor={{ false: colors.inputBorder, true: colors.danger }}
              thumbColor="#fff"
            />
          }
          style={styles.cardRow}
        />
      </Card>

      {/* Privacy */}
      <Text style={styles.sectionTitle}>Privacy & Safety</Text>
      <Card style={styles.card} noPadding>
        <SettingRow
          icon="🛡️"
          title="Privacy Policy"
          subtitle="View our privacy policy"
          onPress={handleViewPrivacyPolicy}
          style={styles.cardRow}
        />
        <View style={styles.divider} />
        <SettingRow
          icon="📋"
          title="Terms of Service"
          onPress={() => Alert.alert('Terms', 'FreeWay Community is for legitimate obstruction resolution only.')}
          style={styles.cardRow}
        />
        <View style={styles.divider} />
        <SettingRow
          icon="📤"
          title="Export My Data"
          subtitle="Download all your data (GDPR Article 15)"
          onPress={handleExportData}
          style={styles.cardRow}
        />
        <View style={styles.divider} />
        <SettingRow
          icon="🗑️"
          title="Delete Account"
          subtitle="Permanently delete your account (GDPR Article 17)"
          onPress={handleDeleteAccount}
          style={{ ...styles.cardRow, opacity: 0.8 }}
        />
        <View style={styles.divider} />
        <SettingRow
          icon="🚩"
          title="Report Abuse"
          subtitle="Report platform misuse or harassment"
          onPress={() => navigation.navigate('ReportUser', { targetUserId: null })}
          style={styles.cardRow}
        />
      </Card>

      {/* App Info */}
      <View style={styles.appInfo}>
        <Text style={styles.appInfoText}>FreeWay Community v1.0.0</Text>
        <Text style={styles.appInfoText}>Built for Indian Roads 🇮🇳</Text>
      </View>

      {/* Sign Out */}
      <Button
        title="Sign Out"
        onPress={handleLogout}
        variant="danger"
        size="lg"
        style={styles.signOutBtn}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  content: { paddingBottom: spacing.xxl },

  header: { alignItems: 'center', paddingVertical: spacing.xl, paddingHorizontal: spacing.lg },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
    position: 'relative',
  },
  avatarText: { fontSize: 32, fontWeight: '800', color: '#fff' },
  avatarBadge: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: colors.success,
    borderWidth: 2,
    borderColor: colors.background,
  },
  name: { fontSize: 22, fontWeight: '800', color: colors.textPrimary },
  vehicleNum: { fontSize: 14, color: colors.accent, fontWeight: '700', marginTop: 4 },
  since: { fontSize: 12, color: colors.textMuted, marginTop: 4 },

  statsRow: {
    flexDirection: 'row',
    marginHorizontal: spacing.lg,
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    paddingVertical: spacing.md,
    marginBottom: spacing.lg,
  },
  statBox: { flex: 1, alignItems: 'center' },
  statNum: { fontSize: 22, fontWeight: '800', color: colors.textPrimary },
  statLabel: { fontSize: 11, color: colors.textMuted, marginTop: 2, textTransform: 'uppercase' },
  statDivider: { width: 1, backgroundColor: colors.divider },

  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.textMuted,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  card: { marginHorizontal: spacing.lg, marginBottom: 0 },
  cardRow: { padding: spacing.md },

  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingIcon: { fontSize: 20, marginRight: spacing.md },
  settingText: { flex: 1 },
  settingTitle: { fontSize: 15, fontWeight: '600', color: colors.textPrimary },
  settingSub: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
  chevron: { fontSize: 18, color: colors.textMuted },

  divider: { height: 1, backgroundColor: colors.divider, marginLeft: 52 },

  appInfo: { alignItems: 'center', paddingVertical: spacing.lg },
  appInfoText: { fontSize: 12, color: colors.textMuted, lineHeight: 18 },

  signOutBtn: { marginHorizontal: spacing.lg, marginTop: 0 },
});
