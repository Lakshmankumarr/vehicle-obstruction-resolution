/**
 * FreeWay Community — ProfileScreen
 * User profile, account info, privacy settings, and logout.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, Switch,
} from 'react-native';
import { useAuth } from '../../context/AuthContext';
import { Card } from '../../components/Card';
import { Button } from '../../components/Button';
import { colors, spacing, radius } from '../../theme';

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

  const handleLogout = () => {
    Alert.alert('Sign Out?', 'You will need to sign in again.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: logout },
    ]);
  };

  const memberSince = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('en-IN', {
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
        <Text style={styles.vehicleNum}>{user?.vehicle_number || '—'}</Text>
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
          <Text style={[styles.statNum, { color: user?.reputation_score >= 4 ? colors.success : colors.warning }]}>
            {user?.reputation_score?.toFixed(1) ?? '—'}
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
          subtitle={user?.phone_number ? `+91 ${user.phone_number}` : 'Not set'}
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
              onValueChange={setNotifications}
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
          subtitle="How we protect your identity"
          onPress={() => Alert.alert('Privacy', 'Your vehicle number is always masked.\nWe never share personal data without consent.')}
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
