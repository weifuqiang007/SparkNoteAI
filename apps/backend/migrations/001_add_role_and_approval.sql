-- ============================================================
-- 迁移编号: 001
-- 迁移名称: add_role_and_approval
-- 创建日期: 2026-05-22
-- 说明: 为 users 表新增角色（role）和审核（approval）相关字段，
--       支持学生/教师/管理员三种角色，以及注册审核流程。
-- ============================================================

-- 1. 新增 role 字段：角色标识（student / teacher / admin）
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'student' NOT NULL;

-- 2. 新增 approval_status 字段：审核状态（pending / approved / rejected）
ALTER TABLE users ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending' NOT NULL;

-- 3. 新增 approval_note 字段：审核备注（admin 填写拒绝原因等）
ALTER TABLE users ADD COLUMN approval_note VARCHAR(500);

-- 4. 新增 approved_by 字段：审核人 ID（外键 → users.id）
ALTER TABLE users ADD COLUMN approved_by INTEGER REFERENCES users(id);

-- 5. 新增 approved_at 字段：审核时间
ALTER TABLE users ADD COLUMN approved_at TIMESTAMP WITH TIME ZONE;

-- 6. 将已有的 admin 账号设置为 admin 角色 + 已审核通过
UPDATE users
SET role = 'admin',
    approval_status = 'approved',
    approved_at = NOW()
WHERE username = 'admin';

-- ============================================================
-- 回滚脚本（如需回滚执行以下语句）:
-- ============================================================
-- ALTER TABLE users DROP COLUMN IF EXISTS role;
-- ALTER TABLE users DROP COLUMN IF EXISTS approval_status;
-- ALTER TABLE users DROP COLUMN IF EXISTS approval_note;
-- ALTER TABLE users DROP COLUMN IF EXISTS approved_by;
-- ALTER TABLE users DROP COLUMN IF EXISTS approved_at;
