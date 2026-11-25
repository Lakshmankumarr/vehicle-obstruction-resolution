/**
 * FreeWay Community — AuthContext
 * Global authentication state: login, logout, token management,
 * and AsyncStorage persistence for tokens across app restarts.
 */
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { api } from "../api/client";
import { registerForPushNotificationsAsync, setupNotificationListeners } from "../services/notificationService";

const AuthContext = createContext(null);

const TOKEN_KEY = "@freeway:access_token";
const REFRESH_KEY = "@freeway:refresh_token";
const USER_KEY = "@freeway:user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

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
          try {
            setUser(JSON.parse(cachedUser));
            setIsAuthenticated(true);
          } catch {
            await AsyncStorage.removeItem(USER_KEY);
          }
        }

        try {
          const meResponse = await api.getMe();

          // Support both direct user response and { user: ... } response
          const me = meResponse?.user || meResponse;

          if (me) {
            setUser(me);
            await AsyncStorage.setItem(USER_KEY, JSON.stringify(me));
            setIsAuthenticated(true);
          }
        } catch {
          await clearSession();
        }
      }
    } catch (err) {
      console.warn("Session restore error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const saveTokens = async (data) => {
    const accessToken =
      data?.tokens?.accessToken ||
      data?.tokens?.access_token ||
      data?.accessToken ||
      data?.access_token;

    const refreshToken =
      data?.tokens?.refreshToken ||
      data?.tokens?.refresh_token ||
      data?.refreshToken ||
      data?.refresh_token;

    if (!accessToken) {
      throw new Error("Authentication succeeded but no access token was returned.");
    }

    api.setToken(accessToken, refreshToken || null);

    await AsyncStorage.setItem(TOKEN_KEY, accessToken);

    if (refreshToken) {
      await AsyncStorage.setItem(REFRESH_KEY, refreshToken);
    } else {
      await AsyncStorage.removeItem(REFRESH_KEY);
    }

    return {
      accessToken,
      refreshToken: refreshToken || null,
    };
  };

  const login = useCallback(async (vehicleNumber, password) => {
    const data = await api.login(vehicleNumber, password);

    await saveTokens(data);

    let me = data?.user;
    if (!me) {
      try {
        const meResponse = await api.getMe();
        me = meResponse?.user || meResponse;
      } catch (e) {
        console.warn("Fallback getMe error:", e);
      }
    }

    if (!me) {
      throw new Error("Login succeeded but user information was not returned.");
    }

    // Ensure both camelCase and snake_case properties are present
    const normalizedUser = {
      ...me,
      vehicle_number: me.vehicle_number || me.primaryVehicle || me.vehicleNumber,
      primaryVehicle: me.primaryVehicle || me.vehicle_number || me.vehicleNumber,
      phone_number: me.phone_number || me.phoneNumber,
      phoneNumber: me.phoneNumber || me.phone_number,
      created_at: me.created_at || me.createdAt,
      createdAt: me.createdAt || me.created_at,
      reputation_score: me.reputation_score !== undefined ? me.reputation_score : me.reputationScore,
      reputationScore: me.reputationScore !== undefined ? me.reputationScore : me.reputation_score,
    };

    setUser(normalizedUser);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(normalizedUser));
    setIsAuthenticated(true);

    // Register for push notifications after successful login
    try {
      await registerForPushNotificationsAsync(normalizedUser.id);
    } catch (e) {
      console.warn("Failed to register for push notifications:", e);
    }

    return normalizedUser;
  }, []);

  const register = useCallback(
    async (vehicleNumber, password, phoneNumber, name) => {
      const data = await api.register(
        vehicleNumber,
        password,
        phoneNumber,
        name
      );

      // Registration returns authentication tokens.
      // Save them immediately so the user is logged in after registration.
      await saveTokens(data);

      const meResponse = data?.user
        ? { user: data.user }
        : await api.getMe();

      const me = meResponse?.user || meResponse;

      if (me) {
        setUser(me);
        await AsyncStorage.setItem(USER_KEY, JSON.stringify(me));
        setIsAuthenticated(true);

        // Register for push notifications after successful registration
        try {
          await registerForPushNotificationsAsync(me.id);
        } catch (e) {
          console.warn("Failed to register for push notifications:", e);
        }
      }

      return me || data;
    },
    []
  );

  const clearSession = async () => {
    api.clearToken();

    await AsyncStorage.multiRemove([
      TOKEN_KEY,
      REFRESH_KEY,
      USER_KEY,
    ]);

    setUser(null);
    setIsAuthenticated(false);
  };

  const logout = useCallback(async () => {
    await clearSession();
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const meResponse = await api.getMe();
      const me = meResponse?.user || meResponse;

      if (me) {
        setUser(me);
        await AsyncStorage.setItem(USER_KEY, JSON.stringify(me));
      }
    } catch (err) {
      console.warn("Refresh user failed:", err);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);

  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return ctx;
}