/**
 * FreeWay Community — Root App Component
 * Sets up NavigationContainer, AuthProvider, and SafeAreaProvider.
 */
import 'react-native-gesture-handler';
import React, { useEffect, useRef } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';

import { AuthProvider, useAuth } from './src/context/AuthContext';
import { setupNotificationListeners } from './src/services/notificationService';
import AppNavigator from './src/navigation/AppNavigator';

// Dark navigation theme matching our design system
const DarkTheme = {
  dark: true,
  colors: {
    primary: '#3B82F6',
    background: '#0B0F19',
    card: '#111827',
    text: '#F9FAFB',
    border: 'rgba(255,255,255,0.08)',
    notification: '#EF4444',
  },
};

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  const navigationRef = useRef(null);

  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      const cleanup = setupNotificationListeners(navigationRef.current);
      return cleanup;
    }
  }, [isAuthenticated, isLoading]);

  return (
    <NavigationContainer ref={navigationRef} theme={DarkTheme}>
      <AppNavigator />
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar style="light" backgroundColor="#0B0F19" />
      <AuthProvider>
        <NavigationContainer theme={DarkTheme}>
          <AppNavigator />
        </NavigationContainer>
      </AuthProvider>
    </SafeAreaProvider>
  );
}
