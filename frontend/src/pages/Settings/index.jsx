import { useState } from 'react'
import { Card, Form, Switch, Select, Radio, Button, Row, Col, Divider, message, InputNumber } from 'antd'
import { SettingOutlined, BgColorsOutlined, BellOutlined, SafetyOutlined } from '@ant-design/icons'

export default function Settings() {
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    message.success('设置已保存')
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="page-container">
      <h2 className="section-title"><SettingOutlined style={{ color: '#00bebd', marginRight: 8 }} />系统设置</h2>

      <Row gutter={[24, 24]}>
        <Col xs={24} md={12}>
          <Card title={<><BgColorsOutlined style={{ marginRight: 8 }} />显示设置</>}>
            <Form layout="vertical" initialValues={{ pageSize: 10, theme: 'light', language: 'zh' }}>
              <Form.Item name="pageSize" label="每页显示条数">
                <Select>
                  <Select.Option value={10}>10 条</Select.Option>
                  <Select.Option value={20}>20 条</Select.Option>
                  <Select.Option value={50}>50 条</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item name="theme" label="主题模式">
                <Radio.Group>
                  <Radio.Button value="light">浅色</Radio.Button>
                  <Radio.Button value="dark">深色</Radio.Button>
                  <Radio.Button value="auto">跟随系统</Radio.Button>
                </Radio.Group>
              </Form.Item>
              <Form.Item name="language" label="语言">
                <Select>
                  <Select.Option value="zh">中文</Select.Option>
                  <Select.Option value="en">English</Select.Option>
                </Select>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title={<><BellOutlined style={{ marginRight: 8 }} />通知设置</>}>
            <Form layout="vertical" initialValues={{ emailNotify: true, taskNotify: true, weeklyReport: false }}>
              <Form.Item name="emailNotify" label="邮件通知" valuePropName="checked">
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              <Form.Item name="taskNotify" label="任务完成通知" valuePropName="checked">
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              <Form.Item name="weeklyReport" label="每周统计报告" valuePropName="checked">
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title={<><SafetyOutlined style={{ marginRight: 8 }} />隐私与安全</>}>
            <Form layout="vertical" initialValues={{ showProfile: true, showFavorites: false, autoLogout: 24 }}>
              <Form.Item name="showProfile" label="公开个人资料" valuePropName="checked">
                <Switch checkedChildren="公开" unCheckedChildren="隐藏" />
              </Form.Item>
              <Form.Item name="showFavorites" label="公开收藏列表" valuePropName="checked">
                <Switch checkedChildren="公开" unCheckedChildren="隐藏" />
              </Form.Item>
              <Form.Item name="autoLogout" label="自动登出时间（小时）">
                <InputNumber min={1} max={72} style={{ width: '100%' }} />
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title={<><SettingOutlined style={{ marginRight: 8 }} />数据设置</>}>
            <Form layout="vertical" initialValues={{ cacheEnabled: true, defaultCity: '', defaultIndustry: '' }}>
              <Form.Item name="cacheEnabled" label="启用查询缓存" valuePropName="checked">
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              <Form.Item name="defaultCity" label="默认搜索城市">
                <Select allowClear placeholder="不限">
                  {['北京', '上海', '深圳', '广州', '杭州', '成都', '武汉', '南京'].map(c => (
                    <Select.Option key={c} value={c}>{c}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item name="defaultIndustry" label="默认搜索行业">
                <Select allowClear placeholder="不限">
                  {['互联网/IT', '金融', '教育培训', '电子商务', '医疗健康', '人工智能'].map(i => (
                    <Select.Option key={i} value={i}>{i}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>

      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <Button type="primary" size="large" onClick={handleSave} style={{ width: 200 }}>
          保存设置
        </Button>
      </div>
    </div>
  )
}
