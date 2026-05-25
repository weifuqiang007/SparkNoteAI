// 管理员 - 注册审批 & 用户管理

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { spacing, typography } from '../../theme';
import { useWebTheme } from '../../hooks/useWebTheme';
import * as adminApi from '../../api/admin';
import type { PendingUser, AdminUser } from '../../api/admin';
import {
  CheckCircleIcon,
  XCircleIcon,
  SearchIcon,
  UsersIcon,
  RefreshCwIcon,
  ShieldIcon,
} from '../../components/icons';

type TabView = 'pending' | 'all';

export const AdminScreen: React.FC = () => {
  const colors = useWebTheme();
  const [activeView, setActiveView] = useState<TabView>('pending');
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [allUsers, setAllUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [filterRole, setFilterRole] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [rejectNote, setRejectNote] = useState<Record<number, string>>({});

  const loadPendingUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminApi.getPendingUsers();
      setPendingUsers(data);
    } catch (e) {
      console.error('加载待审核用户失败:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAllUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminApi.getAllUsers(filterRole || undefined, filterStatus || undefined);
      setAllUsers(data);
    } catch (e) {
      console.error('加载用户列表失败:', e);
    } finally {
      setLoading(false);
    }
  }, [filterRole, filterStatus]);

  useEffect(() => {
    if (activeView === 'pending') {
      loadPendingUsers();
    } else {
      loadAllUsers();
    }
  }, [activeView, loadPendingUsers, loadAllUsers]);

  const handleApprove = async (userId: number) => {
    setActionLoading(userId);
    try {
      await adminApi.approveUser(userId, 'approve', '审核通过');
      loadPendingUsers();
    } catch (e) {
      console.error('审核失败:', e);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (userId: number) => {
    setActionLoading(userId);
    try {
      const note = rejectNote[userId] || '';
      await adminApi.approveUser(userId, 'reject', note || '审核未通过');
      loadPendingUsers();
      setRejectNote(prev => {
        const next = { ...prev };
        delete next[userId];
        return next;
      });
    } catch (e) {
      console.error('拒绝失败:', e);
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleActive = async (userId: number, currentActive: boolean) => {
    setActionLoading(userId);
    try {
      await adminApi.updateUserStatus(userId, !currentActive);
      loadAllUsers();
    } catch (e) {
      console.error('更新状态失败:', e);
    } finally {
      setActionLoading(null);
    }
  };

  const roleLabel = (role: string) => {
    switch (role) {
      case 'student': return '学生';
      case 'teacher': return '教师';
      case 'admin': return '管理员';
      default: return role;
    }
  };

  const statusLabel = (status: string) => {
    switch (status) {
      case 'pending': return '待审核';
      case 'approved': return '已通过';
      case 'rejected': return '已拒绝';
      default: return status;
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case 'pending': return colors.warning;
      case 'approved': return colors.success;
      case 'rejected': return colors.error;
      default: return colors.textSecondary;
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleString('zh-CN', {
        month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <View style={styles.headerLeft}>
          <ShieldIcon size={22} color={colors.primary} />
          <Text style={[styles.headerTitle, { color: colors.text }]}>管理员面板</Text>
        </View>
        <View style={styles.tabs}>
          <TouchableOpacity
            style={[styles.tab, activeView === 'pending' && { backgroundColor: colors.primary + '10', borderBottomColor: colors.primary }]}
            onPress={() => setActiveView('pending')}
          >
            <Text style={[styles.tabText, { color: activeView === 'pending' ? colors.primary : colors.textSecondary }]}>
              待审核 {pendingUsers.length > 0 ? `(${pendingUsers.length})` : ''}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, activeView === 'all' && { backgroundColor: colors.primary + '10', borderBottomColor: colors.primary }]}
            onPress={() => setActiveView('all')}
          >
            <Text style={[styles.tabText, { color: activeView === 'all' ? colors.primary : colors.textSecondary }]}>
              全部用户
            </Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity style={styles.refreshBtn} onPress={activeView === 'pending' ? loadPendingUsers : loadAllUsers}>
          <RefreshCwIcon size={16} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>

      {/* Filters (only for all users view) */}
      {activeView === 'all' && (
        <View style={[styles.filters, { borderBottomColor: colors.border }]}>
          <View style={styles.filterGroup}>
            <SearchIcon size={14} color={colors.textSecondary} />
            <Text style={[styles.filterLabel, { color: colors.textSecondary }]}>角色:</Text>
            {['', 'student', 'teacher', 'admin'].map(r => (
              <TouchableOpacity
                key={r}
                style={[styles.filterChip, { backgroundColor: filterRole === r ? colors.primary + '15' : colors.backgroundSecondary, borderColor: filterRole === r ? colors.primary : colors.border }]}
                onPress={() => setFilterRole(r)}
              >
                <Text style={[styles.filterChipText, { color: filterRole === r ? colors.primary : colors.textSecondary }]}>
                  {r === '' ? '全部' : roleLabel(r)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={styles.filterGroup}>
            <Text style={[styles.filterLabel, { color: colors.textSecondary }]}>状态:</Text>
            {['', 'pending', 'approved', 'rejected'].map(s => (
              <TouchableOpacity
                key={s}
                style={[styles.filterChip, { backgroundColor: filterStatus === s ? colors.primary + '15' : colors.backgroundSecondary, borderColor: filterStatus === s ? colors.primary : colors.border }]}
                onPress={() => setFilterStatus(s)}
              >
                <Text style={[styles.filterChipText, { color: filterStatus === s ? colors.primary : colors.textSecondary }]}>
                  {s === '' ? '全部' : statusLabel(s)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {/* Content */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : activeView === 'pending' ? (
        <PendingUserList
          users={pendingUsers}
          onApprove={handleApprove}
          onReject={handleReject}
          rejectNote={rejectNote}
          onRejectNoteChange={(id, note) => setRejectNote(prev => ({ ...prev, [id]: note }))}
          actionLoading={actionLoading}
          roleLabel={roleLabel}
          formatDate={formatDate}
          colors={colors}
        />
      ) : (
        <AllUserList
          users={allUsers}
          onToggleActive={handleToggleActive}
          actionLoading={actionLoading}
          roleLabel={roleLabel}
          statusLabel={statusLabel}
          statusColor={statusColor}
          formatDate={formatDate}
          colors={colors}
        />
      )}
    </View>
  );
};

// 待审核用户列表
const PendingUserList: React.FC<{
  users: PendingUser[];
  onApprove: (id: number) => void;
  onReject: (id: number) => void;
  rejectNote: Record<number, string>;
  onRejectNoteChange: (id: number, note: string) => void;
  actionLoading: number | null;
  roleLabel: (r: string) => string;
  formatDate: (d: string) => string;
  colors: any;
}> = ({ users, onApprove, onReject, rejectNote, onRejectNoteChange, actionLoading, roleLabel, formatDate, colors }) => {
  if (users.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <CheckCircleIcon size={48} color={colors.textTertiary} />
        <Text style={[styles.emptyText, { color: colors.textSecondary }]}>没有待审核的用户</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
      {users.map(user => (
        <View key={user.id} style={[styles.userCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={styles.userCardHeader}>
            <View style={styles.userInfo}>
              <Text style={[styles.userName, { color: colors.text }]}>{user.username}</Text>
              <Text style={[styles.userEmail, { color: colors.textSecondary }]}>{user.email}</Text>
            </View>
            <View style={[styles.roleBadge, { backgroundColor: colors.primary + '10' }]}>
              <Text style={[styles.roleBadgeText, { color: colors.primary }]}>{roleLabel(user.role)}</Text>
            </View>
          </View>
          <View style={styles.userCardMeta}>
            <Text style={[styles.metaText, { color: colors.textTertiary }]}>注册时间: {formatDate(user.created_at)}</Text>
          </View>

          {/* 拒绝备注输入 */}
          <View style={styles.rejectNoteRow}>
            <TextInput
              style={[styles.rejectNoteInput, { borderColor: colors.border, color: colors.text, backgroundColor: colors.backgroundSecondary }]}
              placeholder="拒绝原因（可选）"
              placeholderTextColor={colors.textTertiary}
              value={rejectNote[user.id] || ''}
              onChangeText={(text) => onRejectNoteChange(user.id, text)}
            />
          </View>

          <View style={styles.actionRow}>
            <TouchableOpacity
              style={[styles.approveBtn, { backgroundColor: colors.success }, actionLoading === user.id && styles.btnDisabled]}
              onPress={() => onApprove(user.id)}
              disabled={actionLoading === user.id}
            >
              {actionLoading === user.id ? <ActivityIndicator size="small" color="#fff" /> : <><CheckCircleIcon size={16} color="#fff" /><Text style={styles.btnText}>通过</Text></>}
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.rejectBtn, { backgroundColor: colors.error }, actionLoading === user.id && styles.btnDisabled]}
              onPress={() => onReject(user.id)}
              disabled={actionLoading === user.id}
            >
              {actionLoading === user.id ? null : <><XCircleIcon size={16} color="#fff" /><Text style={styles.btnText}>拒绝</Text></>}
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

// 全部用户列表
const AllUserList: React.FC<{
  users: AdminUser[];
  onToggleActive: (id: number, active: boolean) => void;
  actionLoading: number | null;
  roleLabel: (r: string) => string;
  statusLabel: (s: string) => string;
  statusColor: (s: string) => string;
  formatDate: (d: string) => string;
  colors: any;
}> = ({ users, onToggleActive, actionLoading, roleLabel, statusLabel, statusColor, formatDate, colors }) => {
  return (
    <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
      {/* Table Header */}
      <View style={[styles.tableHeader, { borderBottomColor: colors.border }]}>
        <Text style={[styles.th, { color: colors.textSecondary, flex: 2 }]}>用户</Text>
        <Text style={[styles.th, { color: colors.textSecondary, flex: 1 }]}>角色</Text>
        <Text style={[styles.th, { color: colors.textSecondary, flex: 1 }]}>审核状态</Text>
        <Text style={[styles.th, { color: colors.textSecondary, flex: 1 }]}>账号状态</Text>
        <Text style={[styles.th, { color: colors.textSecondary, flex: 1 }]}>注册时间</Text>
        <Text style={[styles.th, { color: colors.textSecondary, flex: 0.8 }]}>操作</Text>
      </View>

      {users.map(user => (
        <View key={user.id} style={[styles.tableRow, { borderBottomColor: colors.border }]}>
          <View style={[styles.td, { flex: 2 }]}>
            <Text style={[styles.userName, { color: colors.text }]}>{user.username}</Text>
            <Text style={[styles.userEmail, { color: colors.textTertiary }]}>{user.email}</Text>
          </View>
          <View style={[styles.td, { flex: 1 }]}>
            <View style={[styles.roleBadge, { backgroundColor: colors.primary + '10' }]}>
              <Text style={[styles.roleBadgeText, { color: colors.primary }]}>{roleLabel(user.role)}</Text>
            </View>
          </View>
          <View style={[styles.td, { flex: 1 }]}>
            <View style={[styles.statusBadge, { backgroundColor: statusColor(user.approval_status) + '15' }]}>
              <Text style={[styles.statusText, { color: statusColor(user.approval_status) }]}>{statusLabel(user.approval_status)}</Text>
            </View>
          </View>
          <View style={[styles.td, { flex: 1 }]}>
            <Text style={{ color: user.is_active ? colors.success : colors.error }}>
              {user.is_active ? '启用' : '禁用'}
            </Text>
          </View>
          <View style={[styles.td, { flex: 1 }]}>
            <Text style={[styles.metaText, { color: colors.textTertiary }]}>{formatDate(user.created_at)}</Text>
          </View>
          <View style={[styles.td, { flex: 0.8 }]}>
            {user.role !== 'admin' && (
              <TouchableOpacity
                style={[styles.toggleBtn, { backgroundColor: user.is_active ? colors.error + '10' : colors.success + '10' }]}
                onPress={() => onToggleActive(user.id, user.is_active)}
                disabled={actionLoading === user.id}
              >
                {actionLoading === user.id ? <ActivityIndicator size="small" color={colors.textSecondary} /> : (
                  <Text style={{ color: user.is_active ? colors.error : colors.success, fontSize: 12 }}>
                    {user.is_active ? '禁用' : '启用'}
                  </Text>
                )}
              </TouchableOpacity>
            )}
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  headerLeft: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  tabs: { flexDirection: 'row', gap: spacing.xs },
  tab: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 6,
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabText: { fontSize: 13, fontWeight: '500' },
  refreshBtn: { padding: spacing.xs },
  filters: {
    flexDirection: 'column',
    gap: spacing.sm,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  filterGroup: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs, flexWrap: 'wrap' as const },
  filterLabel: { fontSize: 13, fontWeight: '500' },
  filterChip: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 4,
    borderWidth: 1,
  },
  filterChipText: { fontSize: 12 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scrollContent: { flex: 1, padding: spacing.lg },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: spacing.md },
  emptyText: { fontSize: 15 },

  // User Card (pending view)
  userCard: {
    padding: spacing.md,
    borderRadius: 10,
    borderWidth: 1,
    marginBottom: spacing.md,
  },
  userCardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  userInfo: { gap: 2 },
  userName: { fontSize: 15, fontWeight: '600' },
  userEmail: { fontSize: 13 },
  roleBadge: { paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: 4 },
  roleBadgeText: { fontSize: 12, fontWeight: '500' },
  userCardMeta: { marginTop: spacing.xs },
  metaText: { fontSize: 12 },
  rejectNoteRow: { marginTop: spacing.sm },
  rejectNoteInput: {
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: spacing.sm,
    paddingVertical: 8,
    fontSize: 13,
  },
  actionRow: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md },
  approveBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: spacing.md,
    paddingVertical: 8,
    borderRadius: 6,
  },
  rejectBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: spacing.md,
    paddingVertical: 8,
    borderRadius: 6,
  },
  btnText: { color: '#fff', fontSize: 13, fontWeight: '600' },
  btnDisabled: { opacity: 0.5 },

  // Table (all users view)
  tableHeader: {
    flexDirection: 'row',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
  },
  th: { fontSize: 12, fontWeight: '600', textTransform: 'uppercase' as const },
  tableRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  td: { justifyContent: 'center' },
  statusBadge: { paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: 4, alignSelf: 'flex-start' },
  statusText: { fontSize: 12, fontWeight: '500' },
  toggleBtn: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: 4,
    alignItems: 'center',
  },
});

export default AdminScreen;
