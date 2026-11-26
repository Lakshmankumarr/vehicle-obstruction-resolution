/**
 * FreeWay Community — Notification Service
 * Handles FCM token registration and push notification listeners
 */
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { api } from '../api/client';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const DEVICE_TOKEN_KEY = '@freeway:device_token';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotificationsAsync(userId) {
  let token;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('freeway_notifications', {
      name: 'Freeway Notifications',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#3B82F6',
      sound: 'default',
      enableVibrate: true,
    });
  }

  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== 'granted') {
      console.warn('Failed to get push token for push notification!');
      return;
    }
    token = (await Notifications.getExpoPushTokenAsync({
      projectId: '1bc530e3-7920-4593-b6ac-1cfba6738bfd',
    })).data;
  } else {
    console.warn('Must use physical device for Push Notifications');
  }

  // Register token with backend and persist locally
  if (token) {
    try {
      await api.registerDeviceToken(token, 'ANDROID');
      await AsyncStorage.setItem(DEVICE_TOKEN_KEY, token);
      console.log('FCM token registered with backend:', token);
    } catch (error) {
      console.error('Failed to register device token:', error);
    }
  }

  return token;
}

export function setupNotificationListeners(navigation) {
  // Handle notification received while app is foreground
  const foregroundSubscription = Notifications.addNotificationReceivedListener(notification => {
    console.log('Notification received:', notification);
  });

  // Handle notification tap (when app is background/killed)
  const responseSubscription = Notifications.addNotificationResponseReceivedListener(response => {
    const data = response.notification.request.content.data;
    console.log('Notification response:', response);

    // Navigate based on notification type
    if (data?.type === 'OBSTRUCTION_REQUEST' && data?.requestId) {
      navigation.navigate('RequestDetail', { requestId: data.requestId });
    } else if (data?.type === 'REQUEST_RESPONSE' && data?.requestId) {
      navigation.navigate('RequestDetail', { requestId: data.requestId });
    }
  });

  return () => {
    foregroundSubscription.remove();
    responseSubscription.remove();
  };
}