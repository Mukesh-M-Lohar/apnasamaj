import { StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Text, View } from '@/components/Themed';
import { useAuthStore } from '@/src/store/auth';
import { useEffect, useState } from 'react';
import { apiClient } from '@/src/api/client';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useRouter } from 'expo-router';

export default function TabOneScreen() {
  const { user } = useAuthStore();
  const [events, setEvents] = useState([]);
  const router = useRouter();

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await apiClient.get('/events?limit=5');
      setEvents(response.data.data);
    } catch (error) {
      console.log('Failed to fetch events', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Namaste,</Text>
          <Text style={styles.title}>{user?.first_name || 'Member'}!</Text>
        </View>
        <TouchableOpacity style={styles.profileAvatar} onPress={() => router.push('/(tabs)/profile')}>
          <Text style={styles.avatarText}>{user?.first_name?.[0] || 'U'}</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      
      <Text style={styles.sectionTitle}>Upcoming Events</Text>
      {events.length === 0 ? (
        <Text style={styles.emptyText}>No upcoming events found.</Text>
      ) : (
        events.map((event: any) => (
          <View key={event.id} style={styles.card}>
            <Text style={styles.cardTitle}>{event.title}</Text>
            <Text style={styles.cardSubtitle}>{event.start_date}</Text>
          </View>
        ))
      )}

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    backgroundColor: 'transparent',
  },
  greeting: {
    fontSize: 16,
    color: '#64748b',
    marginBottom: 2,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  profileAvatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#3b82f6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 18,
  },
  separator: {
    marginVertical: 10,
    height: 1,
    width: '100%',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#334155',
  },
  card: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  emptyText: {
    color: '#64748b',
    fontStyle: 'italic',
  },
});

