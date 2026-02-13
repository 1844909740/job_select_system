import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, Select, Tag, Space, message, Card, Row, Col, Statistic, Popconfirm, Spin, Tooltip } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, UserOutlined, TeamOutlined, ArrowUpOutlined, ArrowDownOutlined, SwapOutlined, CrownOutlined } from '@ant-design/icons'
import { userAPI, roleAPI } from '../../api'
import useAuthStore from '../../store/authStore'

export default function Users() {
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('users')
  const [userModalOpen, setUserModalOpen] = useState(false)
  const [roleModalOpen, setRoleModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [editingRole, setEditingRole] = useState(null)
  const [userForm] = Form.useForm()
  const [roleForm] = Form.useForm()

  const currentUser = useAuthStore((s) => s.user)
  const isSuperUser = currentUser?.is_superuser

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const { data: userData } = await userAPI.list()
      const userList = userData.results || userData || []
      setUsers(userList)
      const rolesRes = await roleAPI.list()
      const roleList = rolesRes.data.results || rolesRes.data || []
      setRoles(roleList)
    } catch {} finally { setLoading(false) }
  }

  // === 用户 ===
  const openEditUser = (user) => {
    setEditingUser(user)
    userForm.setFieldsValue({
      username: user.username,
      email: user.email,
      phone: user.phone,
      is_active: user.is_active,
      role_id: user.role?.id,
    })
    setUserModalOpen(true)
  }

  const saveUser = async (values) => {
    try {
      if (editingUser) {
        await userAPI.patch(editingUser.id, values)
        message.success('更新成功')
      } else {
        await userAPI.create(values)
        message.success('创建成功')
      }
      setUserModalOpen(false)
      setEditingUser(null)
      userForm.resetFields()
      loadData()
    } catch (err) {
      message.error('操作失败：' + (err.response?.data?.detail || err.response?.data?.error || '请重试'))
    }
  }

  const deleteUser = async (id) => {
    try {
      await userAPI.delete(id)
      message.success('已删除')
      loadData()
    } catch { message.error('删除失败') }
  }

  // === 权限管理操作 ===
  const promoteUser = async (userId, username) => {
    try {
      await userAPI.promote(userId)
      message.success(`已将 ${username} 升级为管理员`)
      loadData()
    } catch (err) {
      message.error(err.response?.data?.error || '操作失败')
    }
  }

  const demoteUser = async (userId, username) => {
    try {
      await userAPI.demote(userId)
      message.success(`已将 ${username} 降级为普通用户`)
      loadData()
    } catch (err) {
      message.error(err.response?.data?.error || '操作失败')
    }
  }

  const transferSuperuser = async (userId, username) => {
    try {
      await userAPI.transferSuperuser(userId)
      message.success(`已将超级管理员权限转让给 ${username}`)
      // 更新本地用户状态
      const { fetchUser } = useAuthStore.getState()
      await fetchUser()
      loadData()
    } catch (err) {
      message.error(err.response?.data?.error || '操作失败')
    }
  }

  // === 角色 ===
  const openEditRole = (role) => {
    setEditingRole(role)
    roleForm.setFieldsValue({ name: role.name, description: role.description })
    setRoleModalOpen(true)
  }

  const saveRole = async (values) => {
    try {
      if (editingRole) {
        await roleAPI.update(editingRole.id, values)
      } else {
        await roleAPI.create(values)
      }
      message.success('操作成功')
      setRoleModalOpen(false)
      setEditingRole(null)
      roleForm.resetFields()
      loadData()
    } catch { message.error('操作失败') }
  }

  const deleteRole = async (id) => {
    try { await roleAPI.delete(id); message.success('已删除'); loadData() }
    catch { message.error('删除失败') }
  }

  /**
   * 渲染用户身份标签
   */
  const renderUserRole = (record) => {
    if (record.is_superuser) {
      return <Tag icon={<CrownOutlined />} color="gold">超级管理员</Tag>
    }
    if (record.is_staff) {
      return <Tag color="blue">管理员</Tag>
    }
    return <Tag>普通用户</Tag>
  }

  /**
   * 渲染权限操作按钮（仅超级管理员可见）
   */
  const renderAdminActions = (record) => {
    if (!isSuperUser) return null
    // 不能操作自己
    if (record.id === currentUser?.id) return null

    if (record.is_superuser) {
      // 已经是超级管理员，不能操作
      return null
    }

    if (record.is_staff) {
      return (
        <Space>
          <Popconfirm title={`确认将 ${record.username} 降级为普通用户？`} onConfirm={() => demoteUser(record.id, record.username)}>
            <Tooltip title="降级为普通用户">
              <Button size="small" type="link" icon={<ArrowDownOutlined />} danger>降级</Button>
            </Tooltip>
          </Popconfirm>
          <Popconfirm
            title={`确认将超级管理员权限转让给 ${record.username}？转让后你将变为普通管理员。`}
            onConfirm={() => transferSuperuser(record.id, record.username)}
            okText="确认转让"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="转让超级管理员权限">
              <Button size="small" type="link" icon={<SwapOutlined />} style={{ color: '#faad14' }}>转让</Button>
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }

    // 普通用户 → 可以升级
    return (
      <Popconfirm title={`确认将 ${record.username} 升级为管理员？`} onConfirm={() => promoteUser(record.id, record.username)}>
        <Tooltip title="升级为管理员">
          <Button size="small" type="link" icon={<ArrowUpOutlined />} style={{ color: '#52c41a' }}>升级</Button>
        </Tooltip>
      </Popconfirm>
    )
  }

  const userColumns = [
    { title: '用户名', dataIndex: 'username', key: 'username' },
    { title: '邮箱', dataIndex: 'email', key: 'email', ellipsis: true },
    { title: '手机', dataIndex: 'phone', key: 'phone', render: (v) => v || '-' },
    {
      title: '身份', key: 'admin_role', width: 140,
      render: (_, record) => renderUserRole(record),
    },
    // {
    //   title: '角色', dataIndex: 'role', key: 'role',
    //   render: (r) => r ? <Tag color="cyan">{typeof r === 'object' ? r.name : r}</Tag> : <span style={{ color: '#ccc' }}>未分配</span>,
    // },
    {
      title: '状态', dataIndex: 'is_active', key: 'is_active', width: 80,
      render: (v) => <Tag color={v ? 'success' : 'default'}>{v ? '启用' : '禁用'}</Tag>,
    },
    { title: '注册时间', dataIndex: 'date_joined', key: 'date_joined', width: 110, render: (t) => t?.slice(0, 10) },
    {
      title: '操作', key: 'actions', width: 240,
      render: (_, record) => (
        <Space wrap>
          <Button size="small" type="link" icon={<EditOutlined />} onClick={() => openEditUser(record)}>编辑</Button>
          {renderAdminActions(record)}
          {record.id !== currentUser?.id && !(record.is_superuser && !isSuperUser) && (
            <Popconfirm title="确认删除该用户？此操作不可恢复。" onConfirm={() => deleteUser(record.id)}>
              <Button size="small" type="link" danger icon={<DeleteOutlined />}>删除</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  const roleColumns = [
    { title: '角色名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    {
      title: '可使用的权限个数', dataIndex: 'permissions', key: 'perms',
      render: (p) => <Tag color="blue">{Array.isArray(p) ? p.length : 0}</Tag>,
    },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', render: (t) => t?.slice(0, 10) },
    {
      title: '操作', key: 'actions', width: 160,
      render: (_, record) => (
        <Space>
          <Button size="small" type="link" icon={<EditOutlined />} onClick={() => openEditRole(record)}>编辑</Button>
          <Popconfirm title="确认删除？" onConfirm={() => deleteRole(record.id)}>
            <Button size="small" type="link" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      <h2 className="section-title"><TeamOutlined style={{ color: '#00bebd', marginRight: 8 }} />用户管理</h2>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12}>
          <Card><Statistic title="用户总数" value={users.length} prefix={<UserOutlined />} valueStyle={{ color: '#00bebd' }} /></Card>
        </Col>
        <Col xs={12}>
          <Card><Statistic title="身份数" value={users.length} prefix={<TeamOutlined />} valueStyle={{ color: '#722ed1' }} /></Card>
        </Col>
      </Row>

      <div className="table-card">
        <div className="category-tabs" style={{ marginBottom: 0 }}>
          <div className={`category-tab ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>
            <UserOutlined style={{ marginRight: 4 }} />用户列表
          </div>
          {/*<div className={`category-tab ${activeTab === 'roles' ? 'active' : ''}`} onClick={() => setActiveTab('roles')}>*/}
          {/*  <TeamOutlined style={{ marginRight: 4 }} />角色管理*/}
          {/*</div>*/}
          <div style={{ flex: 1 }} />
          {activeTab === 'roles' && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRole(null); roleForm.resetFields(); setRoleModalOpen(true) }}>
              新建角色
            </Button>
          )}
        </div>

        <Spin spinning={loading}>
          {activeTab === 'users' && <Table columns={userColumns} dataSource={users} rowKey="id" pagination={{ pageSize: 10 }} scroll={{ x: 1000 }} />}
          {activeTab === 'roles' && <Table columns={roleColumns} dataSource={roles} rowKey="id" pagination={{ pageSize: 10 }} />}
        </Spin>
      </div>

      {/* 用户弹窗 */}
      <Modal title={editingUser ? '编辑用户' : '新建用户'} open={userModalOpen} onCancel={() => setUserModalOpen(false)} onOk={() => userForm.submit()} okText="保存">
        <Form form={userForm} onFinish={saveUser} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}><Input /></Form.Item>
          {!editingUser && <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}><Input.Password /></Form.Item>}
          <Form.Item name="email" label="邮箱" rules={[{ type: 'email', message: '请输入有效邮箱' }]}><Input /></Form.Item>
          <Form.Item name="phone" label="手机号"><Input /></Form.Item>
          <Form.Item name="role_id" label="角色">
            <Select allowClear placeholder="选择角色">
              {roles.map((r) => <Select.Option key={r.id} value={r.id}>{r.name}</Select.Option>)}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 角色弹窗 */}
      <Modal title={editingRole ? '编辑角色' : '新建角色'} open={roleModalOpen} onCancel={() => setRoleModalOpen(false)} onOk={() => roleForm.submit()} okText="保存">
        <Form form={roleForm} onFinish={saveRole} layout="vertical">
          <Form.Item name="name" label="角色名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Modal>

    </div>
  )
}
