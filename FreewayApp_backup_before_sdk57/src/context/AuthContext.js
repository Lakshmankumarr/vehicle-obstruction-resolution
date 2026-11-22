/**
 * FreeWay Community — AuthContext
 * Global authentication state: login, logout, token management,
 * and SecureStore persistence for tokens across app restarts.
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../api/client';

const AuthContext = createContext(null);

const TOKEN_KEY = '@freeway:access_token';
const REFRESH_KEY = '@freeway:refresh_token';
const USER_KEY = '@freeway:user';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Restore session on app boot
  useEffect(() => {
    restoreSession();
  }, []);

  const restoreSession = async () => {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const refresh = await AsyncStorage.getItem(REFRESH_KEY);
      const cachedUser = await AsyncStorage.getItem(USER_KEY);

      if (token) {
        api.setToken(token, refresh);
        if (cachedUser) {
          setUser(JSON.parse(cachedUser));
          setIsAuthenticated(true);
        }
        // Validate token with server
        try {
          const me = await api.getMe();
          setUser(me);
          await AsyncStorage.setItem(USER_KEY, JSON.stringify(me));
          setIsAuthenticated(true);
        } catch {
          // Token expired — clear session
          await clearSession();
        }
      }
    } catch (err) {
      console.warn('Session restore error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const login = useCallback(async (vehicleNumber, password) => {
    const data = await api.login(vehicleNumber, password);
    api.setToken(data.access_token, data.refresh_token);
    await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
    if (data.refresh_token) {
      await AsyncStorage.setItem(REFRESH_KEY, data.refresh_token);
    }
    const me = await api.getMe();
    setUser(me);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(me));
    setIsAuthenticated(true);
    return me;
  }, []);

  const register = useCallback(async (vehicleNumber, password, phoneNumber, name) => {
    const data = await api.register(vehicleNumber, password, phoneNumber, name);
    return data;
  }, []);

  const logout = useCallback(async () => {
    await clearSession();
  }, []);

  const clearSession = async () => {
    api.clearToken();
    await AsyncStorage.multiRemove([TOKEN_KEY, REFRESH_KEY, USER_KEY]);
    setUser(null);
    setIsAuthenticated(false);
  };

  const refreshUser = useCallback(async () => {
    try {
      const me = await api.getMe();
      setUser(me);
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(me));
    } catch (err) {
      console.warn('Refresh user failed:', err);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
