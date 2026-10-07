/**
 * FreeWay Community API Client.
 * Connects React Native app to the FastAPI backend.
 * Configured for LAN access (192.168.29.87:8000) so physical mobile devices
 * running Expo Go can communicate with the backend seamlessly.
 */
import { Platform } from "react-native";

export const LAN_HOST = "http://192.168.29.87:8000";
export const EMULATOR_HOST = "http://10.0.2.2:8000";
export const LOCAL_HOST = "http://localhost:8000";

// Default host connects to machine's LAN IP so real devices on Wi-Fi work immediately
const DEFAULT_HOST = LAN_HOST;
export const API_BASE_URL = `${DEFAULT_HOST}/api/v1`;

class ApiClient {
  constructor() {
    this.token = null;
    this.refreshToken = null;
  }

  setToken(token, refreshToken = null) {
    this.token = token;
    if (refreshToken) this.refreshToken = refreshToken;
  }

  clearToken() {
    this.token = null;
    this.refreshToken = null;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMsg = data.detail || data.message || `Request failed (${response.status})`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      throw err;
    }
  }

  // --- Auth Endpoints ---
  async register(vehicleNumber, password, phoneNumber = null, name = null) {
    return this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ vehicleNumber, password, phoneNumber, name }),
    });
  }

  async login(vehicleNumber, password) {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ vehicleNumber, password }),
    });
  }

  async getMe() {
    return this.request("/auth/me", { method: "GET" });
  }

  // --- Vehicle Endpoints ---
  async identifyVehicle(vehicleNumber = null, imageBase64 = null) {
    return this.request("/vehicle/identify", {
      method: "POST",
      body: JSON.stringify({ vehicleNumber, image: imageBase64 }),
    });
  }

  async listVehicles() {
    return this.request("/vehicle/", { method: "GET" });
  }

  async addVehicle(vehicleNumber, nickname = null, vehicleType = "CAR") {
    return this.request("/vehicle/", {
      method: "POST",
      body: JSON.stringify({ vehicleNumber, nickname, vehicleType }),
    });
  }

  async deleteVehicle(vehicleId) {
    return this.request(`/vehicle/${vehicleId}`, { method: "DELETE" });
  }

  // --- Obstruction Request Endpoints ---
  async createRequest(targetVehicle, message = null, isEmergency = false) {
    return this.request("/request/", {
      method: "POST",
      body: JSON.stringify({ targetVehicle, message, isEmergency }),
    });
  }

  async respondRequest(requestId, response, responseMessage = null, etaMinutes = null) {
    return this.request("/request/respond", {
      method: "POST",
      body: JSON.stringify({ requestId, response, responseMessage, etaMinutes }),
    });
  }

  async resolveRequest(requestId) {
    return this.request(`/request/${requestId}/resolve`, { method: "POST" });
  }

  async cancelRequest(requestId) {
    return this.request(`/request/${requestId}/cancel`, { method: "POST" });
  }

  async getRequestStatus(requestId) {
    return this.request(`/request/${requestId}`, { method: "GET" });
  }

  async getHistory() {
    return this.request("/request/history", { method: "GET" });
  }

  // --- ALPR Scan ---
  async scanPlate(base64Image) {
    return this.request("/alpr/scan", {
      method: "POST",
      body: JSON.stringify({ image: base64Image }),
    });
  }

  // --- Report Abuse ---
  async submitReport(targetUserId, reason, description = null, requestId = null) {
    return this.request("/report/", {
      method: "POST",
      body: JSON.stringify({ targetUserId, reason, description, requestId }),
    });
  }

  async getHealth() {
    return this.request("/health", { method: "GET" });
  }
}

export const api = new ApiClient();
