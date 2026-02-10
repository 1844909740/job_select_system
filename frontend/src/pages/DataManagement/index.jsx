import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, Select, Tag, Space, message, Card, Row, Col, Statistic, Popconfirm, Spin } from 'antd'
import { PlusOutlined, PlayCircleOutlined, PauseCircleOutlined, DeleteOutlined, DatabaseOutlined, CloudServerOutlined, SyncOutlined } from '@ant-design/icons'
import { dataAPI } from '../../api'

export default function DataManagement() {
  const [tasks, setTasks] = useState([])
  const [sources, setSources] = useState([])
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [sourceModalOpen, setSourceModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('tasks')
  const [form] = Form.useForm()
  const [sourceForm] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [activeTab])

  const loadData = async () => {
    setLoading(true)
    try {
      if (activeTab === 'tasks') {
        const { data } = await dataAPI.tasks.list()
        setTasks(data.results || data || [])
      } else if (activeTab === 'sources') {
        const { data } = await dataAPI.sources.list()
        setSources(data.results || data || [])
      } else {
        const { data } = await dataAPI.records.list()
        setRecords(data.results || data || [])
      }
    } catch {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTask = async (values) => {
    try {
      await dataAPI.tasks.create({
        name: values.name,
        task_type: values.task_type,
        data_source: values.data_source,
        schedule: values.schedule,
        config: values.config ? JSON.parse(values.config) : {},
      })
      message.success('创建成功')
      setModalOpen(false)
      form.resetFields()
      loadData()
    } catch (err) {
      message.error('创建失败：' + (err.response?.data?.detail || '请检查输入'))
    }
  }

  const handleCreateSource = async (values) => {
    try {
      await dataAPI.sources.create(values)
      message.success('创建成功')
      setSourceModalOpen(false)
      sourceForm.resetFields()
      loadData()
    } catch (err) {
      message.error('创建失败')
    }
  }

  const runTask = async (id) => {
    try {
      await dataAPI.tasks.run(id)
      message.success('任务已启动')
      loadData()
    } catch { message.error('启动失败') }
  }

  const pauseTask = async (id) => {
    try {
      await dataAPI.tasks.pause(id)
      message.success('任务已暂停')
      loadData()
    } catch { message.error('暂停失败') }
  }

  const deleteTask = async (id) => {
    try {
      await dataAPI.tasks.delete(id)
      message.success('已删除')
      loadData()
    } catch { message.error('删除失败') }
  }

  const statusMap = {
    pending: { color: 'default', text: '待运行' },
    running: { color: 'processing', text: '运行中' },
    completed: { color: 'success', text: '已完成' },
    failed: { color: 'error', text: '失败' },
    paused: { color: 'warning', text: '已暂停' },
  }

  const taskColumns = [
    { title: '任务名称', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: '类型', dataIndex: 'task_type', key: 'task_type' },
    { title: '调度', dataIndex: 'schedule', key: 'schedule' },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (s) => <Tag color={statusMap[s]?.color}>{statusMap[s]?.text || s}</Tag>,
    },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', render: (t) => t?.slice(0, 16).replace('T', ' ') },
    {
      title: '操作', key: 'actions', width: 180,
      render: (_, record) => (
        <Space>
          <Button size="small" type="link" icon={<PlayCircleOutlined />} onClick={() => runTask(record.id)}>运行</Button>
          <Button size="small" type="link" icon={<PauseCircleOutlined />} onClick={() => pauseTask(record.id)}>暂停</Button>
          <Popconfirm title="确认删除？" onConfirm={() => deleteTask(record.id)}>
            <Button size="small" type="link" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const sourceColumns = [
    { title: '数据源名称', dataIndex: 'name', key: 'name' },
    { title: '类型', dataIndex: 'source_type', key: 'source_type' },
    { title: 'URL', dataIndex: 'url', key: 'url', ellipsis: true },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (v) => <Tag color={v ? 'success' : 'default'}>{v ? '启用' : '禁用'}</Tag> },
  ]

  const recordColumns = [
    { title: '任务', dataIndex: 'task_name', key: 'task_name' },
    { title: '采集数量', dataIndex: 'records_count', key: 'records_count' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s) => <Tag color={statusMap[s]?.color}>{statusMap[s]?.text || s}</Tag> },
    { title: '开始时间', dataIndex: 'start_time', key: 'start_time', render: (t) => t?.slice(0, 16).replace('T', ' ') },
    { title: '结束时间', dataIndex: 'end_time', key: 'end_time', render: (t) => t?.slice(0, 16).replace('T', ' ') },
  ]

  return (
    <div className="page-container">
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={8}>
          <Card><Statistic title="采集任务" value={tasks.length} prefix={<SyncOutlined />} valueStyle={{ color: '#00bebd' }} /></Card>
        </Col>
        <Col xs={8}>
          <Card><Statistic title="数据源" value={sources.length} prefix={<CloudServerOutlined />} valueStyle={{ color: '#722ed1' }} /></Card>
        </Col>
        <Col xs={8}>
          <Card><Statistic title="采集记录" value={records.length} prefix={<DatabaseOutlined />} valueStyle={{ color: '#1890ff' }} /></Card>
        </Col>
      </Row>

      <div className="table-card">
        <div className="category-tabs" style={{ marginBottom: 0 }}>
          {[
            { key: 'tasks', label: '采集任务' },
            { key: 'sources', label: '数据源管理' },
            { key: 'records', label: '采集记录' },
          ].map((tab) => (
            <div key={tab.key} className={`category-tab ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.key)}>
              {tab.label}
            </div>
          ))}
          <div style={{ flex: 1 }} />
          {activeTab === 'tasks' && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>新建任务</Button>
          )}
          {activeTab === 'sources' && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setSourceModalOpen(true)}>新建数据源</Button>
          )}
        </div>

        <Spin spinning={loading}>
          {activeTab === 'tasks' && <Table columns={taskColumns} dataSource={tasks} rowKey="id" pagination={{ pageSize: 10 }} />}
          {activeTab === 'sources' && <Table columns={sourceColumns} dataSource={sources} rowKey="id" pagination={{ pageSize: 10 }} />}
          {activeTab === 'records' && <Table columns={recordColumns} dataSource={records} rowKey="id" pagination={{ pageSize: 10 }} />}
        </Spin>
      </div>

      {/* 新建任务 */}
      <Modal title="新建采集任务" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()} okText="创建">
        <Form form={form} onFinish={handleCreateTask} layout="vertical">
          <Form.Item name="name" label="任务名称" rules={[{ required: true }]}>
            <Input placeholder="请输入任务名称" />
          </Form.Item>
          <Form.Item name="task_type" label="任务类型" rules={[{ required: true }]}>
            <Select placeholder="选择类型">
              <Select.Option value="crawl">网页爬取</Select.Option>
              <Select.Option value="api">API采集</Select.Option>
              <Select.Option value="import">文件导入</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="data_source" label="数据源ID">
            <Input placeholder="关联的数据源ID" />
          </Form.Item>
          <Form.Item name="schedule" label="调度规则">
            <Select placeholder="选择调度频率">
              <Select.Option value="once">单次执行</Select.Option>
              <Select.Option value="hourly">每小时</Select.Option>
              <Select.Option value="daily">每天</Select.Option>
              <Select.Option value="weekly">每周</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="config" label="配置参数 (JSON)">
            <Input.TextArea rows={3} placeholder='{"key": "value"}' />
          </Form.Item>
        </Form>
      </Modal>

      {/* 新建数据源 */}
      <Modal title="新建数据源" open={sourceModalOpen} onCancel={() => setSourceModalOpen(false)} onOk={() => sourceForm.submit()} okText="创建">
        <Form form={sourceForm} onFinish={handleCreateSource} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input placeholder="请输入数据源名称" />
          </Form.Item>
          <Form.Item name="source_type" label="类型" rules={[{ required: true }]}>
            <Select placeholder="选择类型">
              <Select.Option value="website">网站</Select.Option>
              <Select.Option value="api">API</Select.Option>
              <Select.Option value="database">数据库</Select.Option>
              <Select.Option value="file">文件</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="url" label="URL" rules={[{ required: true }]}>
            <Input placeholder="请输入数据源URL" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} placeholder="描述（选填）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
