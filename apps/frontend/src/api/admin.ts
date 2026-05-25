// 管理员 API

import client from './client';

export interface PendingUser {
  id: number;
  username: string;
  email: string;
  role: string;
  approval_status: string;
  created_at: string;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  role: string;
  approval_status: string;
  approval_note: string | null;
  two_factor_enabled: boolean;
  created_at: string;
  updated_at: string | null;
}

export const getPendingUsers = async (): Promise<PendingUser[]> => {
  const response = await client.get('/admin/pending-users');
  return response.data;
};

export const approveUser = async (
  userId: number,
  action: 'approve' | 'reject',
  note?: string,
): Promise<AdminUser> => {
  const response = await client.post('/admin/approve', {
    user_id: userId,
    action,
    note,
  });
  return response.data;
};

export const getAllUsers = async (
  role?: string,
  approvalStatus?: string,
): Promise<AdminUser[]> => {
  const params: Record<string, string> = {};
  if (role) params.role = role;
  if (approvalStatus) params.approval_status = approvalStatus;
  const response = await client.get('/admin/users', { params });
  return response.data;
};

export const updateUserStatus = async (
  userId: number,
  isActive: boolean,
): Promise<AdminUser> => {
  const response = await client.put(`/admin/users/${userId}/status`, {
    is_active: isActive,
  });
  return response.data;
};
