import React, { useEffect, useState } from 'react';
import { StyleSheet, View, Text, FlatList, ActivityIndicator, TouchableOpacity } from 'react-native';
import { apiClient } from '@/src/api/client';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function DonationsScreen() {
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    fetchDonations();
    fetchSummary();
  }, []);

  const fetchDonations = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/donations', { params: { per_page: 20 } });
      setDonations(response.data.data);
    } catch (error) {
      console.log('Failed to fetch donations', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await apiClient.get('/donations/summary');
      setSummary(response.data.data);
    } catch (error) {
      console.log('Failed to fetch donation summary', error);
    }
  };

  const renderItem = ({ item }: { item: any }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <View>
          <Text style={styles.purpose}>{item.purpose}</Text>
          <Text style={styles.donorName}>By: {item.donor_name || 'Anonymous / Member'}</Text>
          <Text style={styles.date}>{item.donation_date}</Text>
        </View>
        <View style={styles.amountContainer}>
          <Text style={styles.amount}>₹{item.amount}</Text>
          <View style={[styles.statusBadge, { backgroundColor: item.status === 'completed' ? '#dcfce7' : '#fef08a' }]}>
            <Text style={[styles.statusText, { color: item.status === 'completed' ? '#166534' : '#854d0e' }]}>
              {item.status.toUpperCase()}
            </Text>
          </View>
        </View>
      </View>
      <View style={styles.cardFooter}>
        <Text style={styles.footerText}>
          <FontAwesome name="bank" size={12} /> {item.payment_mode.toUpperCase()}
        </Text>
        <Text style={styles.receiptText}>{item.receipt_number || 'Processing...'}</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.headerTitle}>Donations Ledger</Text>

      {summary && (
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Total Funds Raised</Text>
          <Text style={styles.summaryAmount}>₹{summary.total_donations}</Text>
          <Text style={styles.summarySub}>From {summary.total_count} contributions</Text>
        </View>
      )}

      {loading && donations.length === 0 ? (
        <ActivityIndicator size="large" color="#3b82f6" style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={donations}
          keyExtractor={(item: any) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContainer}
          ListEmptyComponent={
            <Text style={styles.emptyText}>No donations recorded yet.</Text>
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
  summaryCard: {
    backgroundColor: '#3b82f6',
    marginHorizontal: 20,
    borderRadius: 16,
    padding: 24,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#3b82f6',
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 5,
  },
  summaryTitle: {
    color: '#bfdbfe',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  summaryAmount: {
    color: '#ffffff',
    fontSize: 36,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  summarySub: {
    color: '#eff6ff',
    fontSize: 14,
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  purpose: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 4,
  },
  donorName: {
    fontSize: 14,
    color: '#475569',
    marginBottom: 4,
  },
  date: {
    fontSize: 12,
    color: '#94a3b8',
  },
  amountContainer: {
    alignItems: 'flex-end',
  },
  amount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 8,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingTop: 12,
  },
  footerText: {
    fontSize: 12,
    color: '#64748b',
    fontWeight: '600',
  },
  receiptText: {
    fontSize: 12,
    color: '#3b82f6',
    fontWeight: 'bold',
  },
  emptyText: {
    textAlign: 'center',
    marginTop: 40,
    color: '#64748b',
    fontSize: 16,
  },
});
