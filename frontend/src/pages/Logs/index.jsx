import { useState, useEffect } from 'react'
import { Table, Card, Row, Col, Tag, Input, Select, DatePicker, Space, Spin, message, Empty } from 'antd'
import { FileTextOutlined, WarningOutlined } from '@ant-design/icons'
import { logAPI } from '../../api'

export default function Logs() {
  const [operationLogs, setOperationLogs] = useState([])
  const [systemLogs, setSystemLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('operation')
  const [keyword, setKeyword] = useState('')

  useEffect(() => {
    loadLogs()
  }, [activeTab])

  const loadLogs = async () => {
    setLoading(true)
    try {
      if (activeTab === 'operation') {
        const { data } = await logAPI.operations()
        setOperationLogs(data.results || data || [])
      } else {
        const { data } = await logAPI.system()
        setSystemLogs(data.results || data || [])
      }
    } catch {
      message.error('加载日志失败')
    } finally {
      setLoading(false)
    }
  }

  const methodColors = {
    GET: 'blue', POST: 'green', PUT: 'orange', PATCH: 'gold', DELETE: 'red',
  }

  const statusColors = {
    '成功': 'success', '失败': 'error', '警告': 'warning',
  }

  const levelColors = {
    INFO: 'blue', WARNING: 'gold', ERROR: 'red', DEBUG: 'default', CRITICAL: 'magenta',
  }

  // 操作日志表格列 — 字段名与后端 OperationLogSerializer 保持一致
  const opColumns = [
    { title: '用户', dataIndex: 'user_name', key: 'user_name', width: 100, render: (v) => v || '-' },
    {
      title: '操作类型', dataIndex: 'action_type', key: 'action_type', width: 90,
      render: (v) => <Tag>{v || '-'}</Tag>,
    },
    {
      title: '方法', dataIndex: 'request_method', key: 'request_method', width: 80,
      render: (m) => m ? <Tag color={methodColors[m]}>{m}</Tag> : <span style={{ color: '#ccc' }}>-</span>,
    },
    {
      title: '路径', dataIndex: 'request_path', key: 'request_path', ellipsis: true,
      render: (v) => v || '-',
    },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true, render: (v) => v || '-' },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 80,
      render: (s) => <Tag color={statusColors[s] || 'default'}>{s || '-'}</Tag>,
    },
    {
      title: '状态码', dataIndex: 'response_code', key: 'response_code', width: 80,
      render: (c) => c ? <Tag color={c < 400 ? 'success' : 'error'}>{c}</Tag> : <span style={{ color: '#ccc' }}>-</span>,
    },
    { title: 'IP', dataIndex: 'ip_address', key: 'ip_address', width: 130, render: (v) => v || '-' },
    {
      title: '耗时', dataIndex: 'execution_time', key: 'execution_time', width: 80,
      render: (t) => t != null ? `${Math.round(t)}ms` : '-',
    },
    {
      title: '时间', dataIndex: 'created_at', key: 'created_at', width: 160,
      render: (t) => t?.slice(0, 19).replace('T', ' ') || '-',
    },
  ]

  const sysColumns = [
    {
      title: '级别', dataIndex: 'level', key: 'level', width: 80,
      render: (l) => <Tag color={levelColors[l]}>{l}</Tag>,
    },
    { title: '模块', dataIndex: 'module', key: 'module', width: 120 },
    { title: '消息', dataIndex: 'message', key: 'message', ellipsis: true },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 160, render: (t) => t?.slice(0, 19).replace('T', ' ') },
  ]

  const filteredOpLogs = keyword
    ? operationLogs.filter((l) =>
        l.request_path?.includes(keyword) ||
        l.user_name?.includes(keyword) ||
        l.description?.includes(keyword) ||
        l.action_type?.includes(keyword)
      )
    : operationLogs

  const filteredSysLogs = keyword
    ? systemLogs.filter((l) => l.message?.includes(keyword) || l.module?.includes(keyword))
    : systemLogs

  return (
    <div className="page-container">
      <h2 className="section-title"><FileTextOutlined style={{ color: '#00bebd', marginRight: 8 }} />操作日志</h2>

      <div className="table-card">
        <div className="category-tabs" style={{ marginBottom: 0 }}>
          <div className={`category-tab ${activeTab === 'operation' ? 'active' : ''}`} onClick={() => setActiveTab('operation')}>
            <FileTextOutlined style={{ marginRight: 4 }} />操作日志
          </div>
          <div className={`category-tab ${activeTab === 'system' ? 'active' : ''}`} onClick={() => setActiveTab('system')}>
            <WarningOutlined style={{ marginRight: 4 }} />系统日志
          </div>
          <div style={{ flex: 1 }} />
          <Input.Search
            placeholder="搜索日志..."
            style={{ width: 260 }}
            allowClear
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
        </div>

        <Spin spinning={loading}>
          {activeTab === 'operation' ? (
            <Table columns={opColumns} dataSource={filteredOpLogs} rowKey="id"
              pagination={{ pageSize: 15, showTotal: (t) => `共 ${t} 条` }}
              size="middle" scroll={{ x: 1100 }}
              locale={{ emptyText: <Empty description="暂无操作日志" /> }}
            />
          ) : (
            <Table columns={sysColumns} dataSource={filteredSysLogs} rowKey="id"
              pagination={{ pageSize: 15, showTotal: (t) => `共 ${t} 条` }}
              size="middle" scroll={{ x: 600 }}
              locale={{ emptyText: <Empty description="暂无系统日志" /> }}
            />
          )}
        </Spin>
      </div>
    </div>
  )
}
