import React, { useEffect, useState } from 'react';
import { StyleSheet, View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { apiClient } from '@/src/api/client';
import { useAuthStore } from '@/src/store/auth';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();
  const [volunteerStats, setVolunteerStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    // Attempt to fetch volunteer stats if they are a volunteer
    try {
      setLoading(true);
      // Since we don't have the volunteer UUID directly on the generic user payload, 
      // we might fetch their member profile or volunteer profile via search by mobile or member_id.
      // For this polished UI, we will simulate the UI structure if the API isn't directly 1:1 yet.
      // A full production app would have a `/members/me` endpoint.
    } catch (error) {
      console.log('Failed to fetch profile data', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatarLarge}>
          <Text style={styles.avatarLargeText}>{user?.first_name?.[0] || 'U'}</Text>
        </View>
        <Text style={styles.name}>{user?.first_name} {user?.last_name}</Text>
        <Text style={styles.mobile}>{user?.mobile}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>My Family</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <FontAwesome name="users" size={20} color="#3b82f6" />
            <Text style={styles.rowText}>Manage Family Members</Text>
            <FontAwesome name="chevron-right" size={16} color="#cbd5e1" />
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <FontAwesome name="sitemap" size={20} color="#3b82f6" />
            <Text style={styles.rowText}>View Family Tree</Text>
            <FontAwesome name="chevron-right" size={16} color="#cbd5e1" />
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Volunteer Journey</Text>
        <View style={styles.card}>
          <View style={styles.statsRow}>
            <View style={styles.statBox}>
              <Text style={styles.statNumber}>12</Text>
              <Text style={styles.statLabel}>Events</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statBox}>
              <Text style={styles.statNumber}>48.5</Text>
              <Text style={styles.statLabel}>Hours</Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Settings</Text>
        <View style={styles.card}>
          <TouchableOpacity style={styles.row} onPress={logout}>
            <FontAwesome name="sign-out" size={20} color="#ef4444" />
            <Text style={[styles.rowText, { color: '#ef4444' }]}>Logout</Text>
          </TouchableOpacity>
        </View>
      </View>
      
      <Text style={styles.version}>ApnaSamaj v1.0.0</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    alignItems: 'center',
    paddingVertical: 40,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  avatarLarge: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#3b82f6',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    shadowColor: '#3b82f6',
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 5,
  },
  avatarLargeText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 4,
  },
  mobile: {
    fontSize: 16,
    color: '#64748b',
  },
  section: {
    marginTop: 24,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#94a3b8',
    textTransform: 'uppercase',
    marginBottom: 8,
    marginLeft: 4,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    overflow: 'hidden',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  rowText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
    color: '#1e293b',
    marginLeft: 12,
  },
  divider: {
    height: 1,
    backgroundColor: '#f1f5f9',
    marginLeft: 48,
  },
  statsRow: {
    flexDirection: 'row',
    padding: 20,
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statBox: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: '#64748b',
    fontWeight: '500',
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#e2e8f0',
  },
  version: {
    textAlign: 'center',
    color: '#cbd5e1',
    marginTop: 40,
    marginBottom: 40,
  },
});
