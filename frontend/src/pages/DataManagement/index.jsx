import { useState } from 'react'
import { Button, Card, message, Spin } from 'antd'
import { ThunderboltOutlined, DatabaseOutlined } from '@ant-design/icons'
import { dataAPI } from '../../api'

export default function DataManagement() {
  const [loading, setLoading] = useState(false)

  const handleOneClickCollection = async () => {
    setLoading(true)
    const hide = message.loading('正在采集数据，大约需要 1-3 分钟，请耐心等待...', 0)
    try {
      const { data } = await dataAPI.oneClickCollection()
      hide()
      if (data?.success) {
        message.success(`采集完成！共采集 ${data.total_collected} 条，新增 ${data.total_imported} 条（耗时 ${data.elapsed_seconds}s）`)
      } else {
        message.warning(data?.message || '采集结果未知')
      }
    } catch (err) {
      hide()
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
          从智联招聘(zhaopin.com)自动采集最新岗位数据，覆盖多个行业。采集在后台执行，完成后可查看操作日志。仅管理员和超级管理员可使用。
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
