import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Form, Input, Button, message, Tabs } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons'
import useAuthStore from '../../store/authStore'

export default function Login() {
  const [searchParams] = useSearchParams()
  const defaultTab = searchParams.get('tab') === 'register' ? 'register' : 'login'
  const [activeTab, setActiveTab] = useState(defaultTab)
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuthStore()
  const navigate = useNavigate()

  const onLogin = async (values) => {
    setLoading(true)
    try {
      await login(values.username, values.password)
      message.success('登录成功')
      navigate('/')
    } catch (err) {
      message.error(err.response?.data?.detail || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  const onRegister = async (values) => {
    setLoading(true)
    try {
      await register({
        username: values.username,
        email: values.email,
        phone: values.phone,
        password: values.password,
        password_confirm: values.password_confirm,
      })
      message.success('注册成功，请登录')
      setActiveTab('login')
    } catch (err) {
      const errMsg = err.response?.data
      if (typeof errMsg === 'object') {
        const firstErr = Object.values(errMsg).flat()[0]
        message.error(firstErr || '注册失败')
      } else {
        message.error('注册失败，请稍后重试')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>职位分析系统</h1>
        <p>智能岗位数据采集与分析平台</p>

        <Tabs activeKey={activeTab} onChange={setActiveTab} centered items={[
          {
            key: 'login',
            label: '登录',
            children: (
              <Form onFinish={onLogin} size="large" autoComplete="off">
                <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
                  <Input prefix={<UserOutlined />} placeholder="用户名" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
                  <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" block loading={loading}
                    style={{ height: 48, fontSize: 16, borderRadius: 8 }}>
                    登 录
                  </Button>
                </Form.Item>
              </Form>
            ),
          },
          {
            key: 'register',
            label: '注册',
            children: (
              <Form onFinish={onRegister} size="large" autoComplete="off">
                <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
                  <Input prefix={<UserOutlined />} placeholder="用户名" />
                </Form.Item>
                <Form.Item name="email" rules={[
                  { required: true, message: '请输入邮箱' },
                  { type: 'email', message: '邮箱格式不正确' },
                ]}>
                  <Input prefix={<MailOutlined />} placeholder="邮箱" />
                </Form.Item>
                <Form.Item name="phone">
                  <Input prefix={<PhoneOutlined />} placeholder="手机号（选填）" />
                </Form.Item>
                <Form.Item name="password" rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码至少6位' },
                ]}>
                  <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                </Form.Item>
                <Form.Item name="password_confirm" dependencies={['password']} rules={[
                  { required: true, message: '请确认密码' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) return Promise.resolve()
                      return Promise.reject(new Error('两次密码不一致'))
                    },
                  }),
                ]}>
                  <Input.Password prefix={<LockOutlined />} placeholder="确认密码" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" block loading={loading}
                    style={{ height: 48, fontSize: 16, borderRadius: 8 }}>
                    注 册
                  </Button>
                </Form.Item>
              </Form>
            ),
          },
        ]} />
      </div>
    </div>
  )
}
