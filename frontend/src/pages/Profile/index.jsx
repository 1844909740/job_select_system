import { useState, useEffect } from 'react'
import { Card, Form, Input, Button, Avatar, Row, Col, Descriptions, Tag, message, Divider, Statistic } from 'antd'
import { UserOutlined, MailOutlined, PhoneOutlined, EditOutlined, SaveOutlined, HeartOutlined, SearchOutlined, RobotOutlined } from '@ant-design/icons'
import useAuthStore from '../../store/authStore'
import { authAPI, positionAPI, aiAPI } from '../../api'

export default function Profile() {
  const { user, fetchUser } = useAuthStore()
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({ favorites: 0, aiTasks: 0 })
  const [form] = Form.useForm()

  useEffect(() => {
    if (user) {
      form.setFieldsValue({ username: user.username, email: user.email, phone: user.phone })
    }
    loadStats()
  }, [user])

  const loadStats = async () => {
    try {
      const [favRes, aiRes] = await Promise.allSettled([
        positionAPI.favorites(),
        aiAPI.tasks.list(),
      ])
      setStats({
        favorites: favRes.status === 'fulfilled' ? (favRes.value.data.count ?? favRes.value.data.length ?? 0) : 0,
        aiTasks: aiRes.status === 'fulfilled' ? (aiRes.value.data.count ?? aiRes.value.data.results?.length ?? 0) : 0,
      })
    } catch {}
  }

  const handleSave = async (values) => {
    setLoading(true)
    try {
      await authAPI.updateProfile(values)
      await fetchUser()
      message.success('个人资料更新成功')
      setEditing(false)
    } catch (err) {
      message.error('更新失败：' + (err.response?.data?.detail || '请稍后重试'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <h2 className="section-title"><UserOutlined style={{ color: '#00bebd', marginRight: 8 }} />个人资料</h2>

      <Row gutter={[24, 24]}>
        {/* 左侧：用户信息卡 */}
        <Col xs={24} md={8}>
          <Card style={{ textAlign: 'center' }}>
            <Avatar size={80} icon={<UserOutlined />} style={{ backgroundColor: '#00bebd', marginBottom: 16 }} />
            <h3 style={{ marginBottom: 4 }}>{user?.username}</h3>
            <p style={{ color: '#999', fontSize: 13 }}>{user?.email}</p>
            {user?.is_superuser && <Tag color="gold">超级管理员</Tag>}
            {user?.is_staff && !user?.is_superuser && <Tag color="blue">管理员</Tag>}
            {!user?.is_staff && !user?.is_superuser && <Tag color="green">普通用户</Tag>}

            <Divider />

            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic title="收藏岗位" value={stats.favorites} prefix={<HeartOutlined />} valueStyle={{ color: '#fe574a', fontSize: 20 }} />
              </Col>
              <Col span={12}>
                <Statistic title="AI分析" value={stats.aiTasks} prefix={<RobotOutlined />} valueStyle={{ color: '#00bebd', fontSize: 20 }} />
              </Col>
            </Row>
          </Card>

          <Card style={{ marginTop: 16 }} title="账户信息" size="small">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="用户ID">{user?.id}</Descriptions.Item>
              <Descriptions.Item label="注册时间">{user?.date_joined?.slice(0, 10) || user?.created_at?.slice(0, 10)}</Descriptions.Item>
              <Descriptions.Item label="角色">
                {user?.role ? (typeof user.role === 'object' ? user.role.name : user.role) : '未分配'}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={user?.is_active !== false ? 'success' : 'default'}>
                  {user?.is_active !== false ? '正常' : '已禁用'}
                </Tag>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 右侧：编辑表单 */}
        <Col xs={24} md={16}>
          <Card
            title="基本信息"
            extra={
              !editing ? (
                <Button icon={<EditOutlined />} onClick={() => setEditing(true)}>编辑</Button>
              ) : (
                <Button onClick={() => { setEditing(false); form.setFieldsValue({ username: user?.username, email: user?.email, phone: user?.phone }) }}>取消</Button>
              )
            }
          >
            <Form form={form} onFinish={handleSave} layout="vertical" disabled={!editing}>
              <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
                <Input prefix={<UserOutlined />} size="large" />
              </Form.Item>
              <Form.Item name="email" label="邮箱" rules={[{ type: 'email', message: '邮箱格式不正确' }]}>
                <Input prefix={<MailOutlined />} size="large" />
              </Form.Item>
              <Form.Item name="phone" label="手机号">
                <Input prefix={<PhoneOutlined />} size="large" />
              </Form.Item>
              {editing && (
                <Form.Item>
                  <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading} size="large">
                    保存修改
                  </Button>
                </Form.Item>
              )}
            </Form>
          </Card>

          <Card title="修改密码" style={{ marginTop: 16 }}>
            <Form layout="vertical" onFinish={async (v) => {
              try {
                await authAPI.updateProfile({ password: v.new_password })
                message.success('密码修改成功，请重新登录')
              } catch {
                message.error('修改失败')
              }
            }}>
              <Form.Item name="new_password" label="新密码" rules={[{ required: true, min: 6, message: '密码至少6位' }]}>
                <Input.Password size="large" placeholder="输入新密码" />
              </Form.Item>
              <Form.Item name="confirm_password" label="确认密码" dependencies={['new_password']} rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) return Promise.resolve()
                    return Promise.reject(new Error('两次密码不一致'))
                  },
                }),
              ]}>
                <Input.Password size="large" placeholder="再次输入密码" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" size="large">修改密码</Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
