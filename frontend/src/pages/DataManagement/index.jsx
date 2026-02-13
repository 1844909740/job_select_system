import { useState } from 'react'
import { Button, Card, message, Spin } from 'antd'
import { ThunderboltOutlined, DatabaseOutlined } from '@ant-design/icons'
import { dataAPI } from '../../api'

export default function DataManagement() {
  const [loading, setLoading] = useState(false)

  const handleOneClickCollection = async () => {
    setLoading(true)
    try {
      const { data } = await dataAPI.oneClickCollection()
      message.success(data?.message || '数据采集完成！已成功生成15000条岗位数据')
    } catch (err) {
      message.error(err.response?.data?.error || '一键采集失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <h2 className="section-title">
        <DatabaseOutlined style={{ color: '#00bebd', marginRight: 8 }} />数据采集
      </h2>
      <Card style={{ maxWidth: 480, margin: '40px auto', textAlign: 'center' }}>
        <p style={{ color: '#666', marginBottom: 24 }}>
          点击下方按钮将调用系统生成 15000 条岗位数据，覆盖现有岗位数据。仅管理员和超级管理员可使用。
        </p>
        <Button
          type="primary"
          size="large"
          icon={<ThunderboltOutlined />}
          loading={loading}
          onClick={handleOneClickCollection}
          style={{ minWidth: 160 }}
        >
          一键采集
        </Button>
      </Card>
    </div>
  )
}
