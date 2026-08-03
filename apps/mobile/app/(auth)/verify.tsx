import React, { useState } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { apiClient } from '@/src/api/client';
import { useAuthStore } from '@/src/store/auth';

export default function VerifyScreen() {
  const { mobile, devOtp } = useLocalSearchParams<{ mobile: string, devOtp?: string }>();
  const [otp, setOtp] = useState(devOtp || '');
  const [loading, setLoading] = useState(false);
  const { login } = useAuthStore();

  const handleVerify = async () => {
    if (!otp || otp.length < 4) {
      Alert.alert('Error', 'Please enter a valid OTP');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        mobile: mobile,
        otp: otp,
        device_name: "Mobile App"
      };

      const response = await apiClient.post('/auth/otp/verify', payload);

      const { access_token, user, tenant } = response.data.data;
      const tenantId = tenant?.id || "";

      await login(access_token, tenantId, user);
      // The _layout.tsx effect will automatically redirect to /(tabs)/ based on the store update.
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.message || 'Failed to verify OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Verify OTP</Text>
      <Text style={styles.subtitle}>Enter the code sent to {mobile}</Text>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Enter OTP"
          keyboardType="number-pad"
          maxLength={6}
          value={otp}
          onChangeText={setOtp}
          placeholderTextColor="#9ca3af"
          textAlign="center"
        />
      </View>

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleVerify}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Verify & Login</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#f8fafc',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#0f172a',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
    marginBottom: 48,
  },
  inputContainer: {
    marginBottom: 24,
    alignItems: 'center',
  },
  input: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 8,
    padding: 16,
    fontSize: 24,
    letterSpacing: 8,
    color: '#0f172a',
    width: '80%',
  },
  button: {
    backgroundColor: '#3b82f6',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#93c5fd',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
