/**
 * FreeWay Community — Tab Navigator
 * Bottom tab bar for the main authenticated app sections.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import DashboardScreen from '../screens/main/DashboardScreen';
import HistoryScreen from '../screens/main/HistoryScreen';
import VehiclesScreen from '../screens/main/VehiclesScreen';
import ProfileScreen from '../screens/main/ProfileScreen';
import { colors } from '../theme';

const Tab = createBottomTabNavigator();

function TabIcon({ emoji, label, focused }) {
  return (
    <View style={[styles.tabItem, focused && styles.tabItemFocused]}>
      <Text style={[styles.tabEmoji, focused && styles.tabEmojiFocused]}>{emoji}</Text>
      <Text style={[styles.tabLabel, focused && styles.tabLabelFocused]}>{label}</Text>
    </View>
  );
}

export default function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.backgroundSecondary, shadowColor: 'transparent', borderBottomWidth: 1, borderBottomColor: colors.divider },
        headerTintColor: colors.textPrimary,
        headerTitleStyle: { fontWeight: '700', fontSize: 17 },
        tabBarStyle: styles.tabBar,
        tabBarShowLabel: false,
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          headerTitle: '🚗 FreeWay',
          tabBarIcon: ({ focused }) => <TabIcon emoji="🏠" label="Home" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="History"
        component={HistoryScreen}
        options={{
          headerTitle: 'Request History',
          tabBarIcon: ({ focused }) => <TabIcon emoji="📋" label="History" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Vehicles"
        component={VehiclesScreen}
        options={{
          headerTitle: 'My Vehicles',
          tabBarIcon: ({ focused }) => <TabIcon emoji="🚗" label="Vehicles" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          headerTitle: 'My Profile',
          tabBarIcon: ({ focused }) => <TabIcon emoji="👤" label="Profile" focused={focused} />,
        }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: colors.backgroundSecondary,
    borderTopColor: colors.divider,
    borderTopWidth: 1,
    height: 64,
    paddingBottom: 8,
  },
  tabItem: { alignItems: 'center', paddingTop: 6, paddingHorizontal: 12 },
  tabItemFocused: {},
  tabEmoji: { fontSize: 22, opacity: 0.5 },
  tabEmojiFocused: { opacity: 1 },
  tabLabel: { fontSize: 10, color: colors.textMuted, marginTop: 2 },
  tabLabelFocused: { color: colors.primary, fontWeight: '700' },
});
