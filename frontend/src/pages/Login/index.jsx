import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Form, Input, Button, message, Tabs, Progress, Typography } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined, SafetyOutlined } from '@ant-design/icons'
import useAuthStore from '../../store/authStore'

const { Text } = Typography

/**
 * 计算密码强度（0-100）
 */
function getPasswordStrength(password) {
  if (!password) return { percent: 0, label: '', color: '' }
  let score = 0
  if (password.length >= 6) score += 20
  if (password.length >= 10) score += 10
  if (/[a-z]/.test(password)) score += 15
  if (/[A-Z]/.test(password)) score += 15
  if (/[0-9]/.test(password)) score += 20
  if (/[^a-zA-Z0-9]/.test(password)) score += 20

  if (score <= 30) return { percent: score, label: '弱', color: '#f5222d' }
  if (score <= 60) return { percent: score, label: '中', color: '#faad14' }
  return { percent: score, label: '强', color: '#52c41a' }
}

export default function Login() {
  const [searchParams] = useSearchParams()
  const defaultTab = searchParams.get('tab') === 'register' ? 'register' : 'login'
  const [activeTab, setActiveTab] = useState(defaultTab)
  const [loading, setLoading] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState({ percent: 0, label: '', color: '' })
  const { login, register } = useAuthStore()
  const navigate = useNavigate()
  const [loginForm] = Form.useForm()
  const [registerForm] = Form.useForm()

  const onLogin = async (values) => {
    setLoading(true)
    try {
      await login(values.username, values.password)
      message.success('登录成功，正在跳转...')
      navigate('/')
    } catch (err) {
      const errData = err.response?.data
      if (errData?.detail) {
        message.error(errData.detail)
      } else if (errData?.non_field_errors) {
        message.error(errData.non_field_errors[0])
      } else {
        message.error('登录失败，请检查用户名和密码是否正确')
      }
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
        phone: values.phone || '',
        password: values.password,
        password_confirm: values.password_confirm,
      })
      message.success('注册成功！请使用新账号登录')
      // 注册成功后自动切换到登录tab，并填入用户名
      setActiveTab('login')
      loginForm.setFieldsValue({ username: values.username })
      registerForm.resetFields()
      setPasswordStrength({ percent: 0, label: '', color: '' })
    } catch (err) {
      const errData = err.response?.data
      if (errData?.errors) {
        // 后端返回了字段级的错误，设置到表单对应字段上
        const fieldErrors = Object.entries(errData.errors).map(([field, messages]) => ({
          name: field,
          errors: Array.isArray(messages) ? messages : [messages],
        }))
        registerForm.setFields(fieldErrors)

        // 同时用 message 提示第一个错误
        const firstError = Object.values(errData.errors).flat()[0]
        if (firstError) message.error(firstError)
      } else if (errData?.error) {
        message.error(errData.error)
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
              <Form form={loginForm} onFinish={onLogin} size="large" autoComplete="off">
                <Form.Item
                  name="username"
                  rules={[{ required: true, message: '请输入用户名' }]}
                >
                  <Input prefix={<UserOutlined />} placeholder="用户名" allowClear />
                </Form.Item>
                <Form.Item
                  name="password"
                  rules={[{ required: true, message: '请输入密码' }]}
                >
                  <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" block loading={loading}
                    style={{ height: 48, fontSize: 16, borderRadius: 8 }}>
                    登 录
                  </Button>
                </Form.Item>
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary">
                    还没有账号？
                    <a onClick={() => setActiveTab('register')} style={{ color: '#00bebd', marginLeft: 4 }}>
                      立即注册
                    </a>
                  </Text>
                </div>
              </Form>
            ),
          },
          {
            key: 'register',
            label: '注册',
            children: (
              <Form form={registerForm} onFinish={onRegister} size="large" autoComplete="off" scrollToFirstError>
                <Form.Item
                  name="username"
                  rules={[
                    { required: true, message: '请输入用户名' },
                    { min: 3, message: '用户名至少3个字符' },
                    { max: 20, message: '用户名最多20个字符' },
                    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文' },
                  ]}
                  hasFeedback
                >
                  <Input prefix={<UserOutlined />} placeholder="用户名（3-20个字符，字母/数字/下划线/中文）" allowClear />
                </Form.Item>
                <Form.Item
                  name="email"
                  rules={[
                    { required: true, message: '请输入邮箱地址' },
                    { type: 'email', message: '请输入有效的邮箱地址，例如 user@example.com' },
                  ]}
                  hasFeedback
                >
                  <Input prefix={<MailOutlined />} placeholder="邮箱地址" allowClear />
                </Form.Item>
                <Form.Item
                  name="phone"
                  rules={[
                    { required: true, message: '请填写手机号' },
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的11位手机号' },
                  ]}
                  hasFeedback
                >
                  <Input prefix={<PhoneOutlined />} placeholder="手机号" maxLength={11} allowClear />
                </Form.Item>
                <Form.Item
                  name="password"
                  rules={[
                    { required: true, message: '请输入密码' },
                    { min: 6, message: '密码至少6位' },
                    { max: 32, message: '密码最多32位' },
                    {
                      validator(_, value) {
                        if (!value) return Promise.resolve()
                        if (value && /^\d+$/.test(value)) return Promise.reject(new Error('密码不能是纯数字，请包含字母'))
                        if (value && /^[a-zA-Z]+$/.test(value)) return Promise.reject(new Error('密码不能是纯字母，请包含数字'))
                        return Promise.resolve()
                      }
                    },
                  ]}
                  hasFeedback
                >
                  <Input.Password
                    prefix={<SafetyOutlined />}
                    placeholder="密码（6-32位，需包含字母和数字）"
                    onChange={(e) => setPasswordStrength(getPasswordStrength(e.target.value))}
                  />
                </Form.Item>
                {passwordStrength.percent > 0 && (
                  <div style={{ marginTop: -16, marginBottom: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 12, color: '#999', whiteSpace: 'nowrap' }}>密码强度：</span>
                      <Progress
                        percent={passwordStrength.percent}
                        size="small"
                        strokeColor={passwordStrength.color}
                        showInfo={false}
                        style={{ flex: 1 }}
                      />
                      <span style={{ fontSize: 12, color: passwordStrength.color, fontWeight: 600, whiteSpace: 'nowrap' }}>
                        {passwordStrength.label}
                      </span>
                    </div>
                  </div>
                )}
                <Form.Item
                  name="password_confirm"
                  dependencies={['password']}
                  rules={[
                    { required: true, message: '请再次输入密码确认' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('password') === value) return Promise.resolve()
                        return Promise.reject(new Error('两次输入的密码不一致'))
                      },
                    }),
                  ]}
                  hasFeedback
                >
                  <Input.Password prefix={<LockOutlined />} placeholder="确认密码" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" block loading={loading}
                    style={{ height: 48, fontSize: 16, borderRadius: 8 }}>
                    注 册
                  </Button>
                </Form.Item>
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary">
                    已有账号？
                    <a onClick={() => setActiveTab('login')} style={{ color: '#00bebd', marginLeft: 4 }}>
                      返回登录
                    </a>
                  </Text>
                </div>
              </Form>
            ),
          },
        ]} />
      </div>
    </div>
  )
}
