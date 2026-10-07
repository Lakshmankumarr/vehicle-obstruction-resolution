/**
 * FreeWay Community — AppNavigator
 * Root navigator. Switches between Auth stack and Main tabs
 * based on authentication state from AuthContext.
 */
import React from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../context/AuthContext';

// Auth Screens
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';

// Main / Tabbed
import TabNavigator from './TabNavigator';

// Non-tab screens accessible from anywhere
import NewRequestScreen from '../screens/main/NewRequestScreen';
import RequestDetailScreen from '../screens/main/RequestDetailScreen';
import ReportUserScreen from '../screens/main/ReportUserScreen';

import { colors } from '../theme';

const Stack = createNativeStackNavigator();

function SplashScreen() {
  return (
    <View style={styles.splash}>
      <ActivityIndicator color={colors.primary} size="large" />
    </View>
  );
}

export default function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <SplashScreen />;

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
        animation: 'fade_from_bottom',
      }}
    >
      {isAuthenticated ? (
        // === Authenticated Stack ===
        <>
          <Stack.Screen name="Tabs" component={TabNavigator} />
          <Stack.Screen
            name="NewRequest"
            component={NewRequestScreen}
            options={{ animation: 'slide_from_bottom' }}
          />
          <Stack.Screen
            name="RequestDetail"
            component={RequestDetailScreen}
            options={{ animation: 'slide_from_right' }}
          />
          <Stack.Screen
            name="ReportUser"
            component={ReportUserScreen}
            options={{ animation: 'slide_from_bottom' }}
          />
        </>
      ) : (
        // === Auth Stack ===
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Register" component={RegisterScreen} />
        </>
      )}
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  splash: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
