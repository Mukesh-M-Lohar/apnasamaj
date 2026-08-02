import React, { useEffect, useState } from 'react';
import { StyleSheet, View, Text, FlatList, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import { apiClient } from '@/src/api/client';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function EventsScreen() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/events', { params: { per_page: 50 } });
      setEvents(response.data.data);
    } catch (error) {
      console.log('Failed to fetch events', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRSVP = async (eventId: string) => {
    try {
      await apiClient.post(`/events/${eventId}/register`);
      Alert.alert("Success", "You have successfully RSVP'd for this event!");
      fetchEvents(); // Refresh to update spots
    } catch (error: any) {
      Alert.alert("Error", error.response?.data?.message || "Failed to RSVP.");
    }
  };

  const renderItem = ({ item }: { item: any }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.title}>{item.title}</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{item.event_type.toUpperCase()}</Text>
        </View>
      </View>
      <Text style={styles.description} numberOfLines={2}>{item.description}</Text>
      
      <View style={styles.infoRow}>
        <FontAwesome name="calendar" size={14} color="#64748b" />
        <Text style={styles.infoText}>{new Date(item.start_date).toLocaleString()}</Text>
      </View>
      
      <View style={styles.infoRow}>
        <FontAwesome name="map-marker" size={14} color="#64748b" />
        <Text style={styles.infoText}>{item.location}</Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.spotsText}>
          {item.registered_count} / {item.max_attendees} spots filled
        </Text>
        <TouchableOpacity 
          style={styles.rsvpButton} 
          onPress={() => handleRSVP(item.id)}
          disabled={item.registered_count >= item.max_attendees}
        >
          <Text style={styles.rsvpText}>
            {item.registered_count >= item.max_attendees ? "FULL" : "RSVP"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.headerTitle}>Community Events</Text>

      {loading && events.length === 0 ? (
        <ActivityIndicator size="large" color="#3b82f6" style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={events}
          keyExtractor={(item: any) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContainer}
          ListEmptyComponent={
            <Text style={styles.emptyText}>No upcoming events.</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
    paddingTop: 40,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#0f172a',
    marginHorizontal: 20,
    marginBottom: 16,
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    flex: 1,
    marginRight: 8,
  },
  badge: {
    backgroundColor: '#eff6ff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  description: {
    fontSize: 14,
    color: '#475569',
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  infoText: {
    fontSize: 13,
    color: '#64748b',
    marginLeft: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
  },
  spotsText: {
    fontSize: 13,
    color: '#94a3b8',
    fontWeight: '500',
  },
  rsvpButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  rsvpText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  emptyText: {
    textAlign: 'center',
    marginTop: 40,
    color: '#64748b',
    fontSize: 16,
  },
});
