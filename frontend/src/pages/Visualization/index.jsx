import { useState, useEffect } from 'react'
import { Card, Row, Col, Button, Modal, Form, Input, Select, Tag, Space, message, Spin, Empty, Popconfirm } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, DashboardOutlined, BarChartOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { vizAPI } from '../../api'

export default function Visualization() {
  const [dashboards, setDashboards] = useState([])
  const [charts, setCharts] = useState([])
  const [loading, setLoading] = useState(false)
  const [dashModalOpen, setDashModalOpen] = useState(false)
  const [chartModalOpen, setChartModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('dashboards')
  const [dashForm] = Form.useForm()
  const [chartForm] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [activeTab])

  const loadData = async () => {
    setLoading(true)
    try {
      if (activeTab === 'dashboards') {
        const { data } = await vizAPI.dashboards.list()
        setDashboards(data.results || data || [])
      } else {
        const { data } = await vizAPI.charts.list()
        setCharts(data.results || data || [])
      }
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  const createDashboard = async (values) => {
    try {
      await vizAPI.dashboards.create(values)
      message.success('仪表盘创建成功')
      setDashModalOpen(false)
      dashForm.resetFields()
      loadData()
    } catch { message.error('创建失败') }
  }

  const deleteDashboard = async (id) => {
    try {
      await vizAPI.dashboards.delete(id)
      message.success('已删除')
      loadData()
    } catch { message.error('删除失败') }
  }

  const createChart = async (values) => {
    try {
      await vizAPI.charts.create({
        ...values,
        config: values.config ? JSON.parse(values.config) : {},
      })
      message.success('图表创建成功')
      setChartModalOpen(false)
      chartForm.resetFields()
      loadData()
    } catch { message.error('创建失败') }
  }

  const deleteChart = async (id) => {
    try {
      await vizAPI.charts.delete(id)
      message.success('已删除')
      loadData()
    } catch { message.error('删除失败') }
  }

  const getChartPreview = (chart) => {
    const mockData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    const mockValues = mockData.map(() => Math.floor(Math.random() * 1000))
    const type = chart.chart_type || 'bar'
    return {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: mockData },
      yAxis: { type: 'value' },
      series: [{ data: mockValues, type: type === 'pie' ? 'bar' : type, smooth: true, itemStyle: { color: '#00bebd' } }],
      grid: { left: '10%', right: '5%', bottom: '10%', top: '10%' },
    }
  }

  return (
    <div className="page-container">
      <h2 className="section-title"><DashboardOutlined style={{ color: '#00bebd', marginRight: 8 }} />数据可视化</h2>

      <div className="table-card">
        <div className="category-tabs" style={{ marginBottom: 0 }}>
          <div className={`category-tab ${activeTab === 'dashboards' ? 'active' : ''}`} onClick={() => setActiveTab('dashboards')}>仪表盘</div>
          <div className={`category-tab ${activeTab === 'charts' ? 'active' : ''}`} onClick={() => setActiveTab('charts')}>图表组件</div>
          <div style={{ flex: 1 }} />
          {activeTab === 'dashboards' && <Button type="primary" icon={<PlusOutlined />} onClick={() => setDashModalOpen(true)}>新建仪表盘</Button>}
          {activeTab === 'charts' && <Button type="primary" icon={<PlusOutlined />} onClick={() => setChartModalOpen(true)}>新建图表</Button>}
        </div>

        <Spin spinning={loading}>
          {activeTab === 'dashboards' ? (
            dashboards.length === 0 ? <Empty description="暂无仪表盘" style={{ padding: 60 }} /> : (
              <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
                {dashboards.map((d) => (
                  <Col xs={24} sm={12} md={8} key={d.id}>
                    <Card
                      actions={[
                        <EditOutlined key="edit" />,
                        <Popconfirm key="del" title="确认删除？" onConfirm={() => deleteDashboard(d.id)}>
                          <DeleteOutlined style={{ color: '#ff4d4f' }} />
                        </Popconfirm>,
                      ]}
                    >
                      <Card.Meta
                        title={d.name || d.title}
                        description={d.description || '暂无描述'}
                      />
                      <div style={{ marginTop: 12 }}>
                        <Tag color={d.is_public ? 'green' : 'orange'}>{d.is_public ? '公开' : '私有'}</Tag>
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            )
          ) : (
            charts.length === 0 ? <Empty description="暂无图表" style={{ padding: 60 }} /> : (
              <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
                {charts.map((c) => (
                  <Col xs={24} sm={12} key={c.id}>
                    <Card
                      title={<><BarChartOutlined style={{ marginRight: 8 }} />{c.name || c.title}</>}
                      extra={
                        <Popconfirm title="确认删除？" onConfirm={() => deleteChart(c.id)}>
                          <Button type="text" danger icon={<DeleteOutlined />} />
                        </Popconfirm>
                      }
                    >
                      <Tag color="cyan">{c.chart_type}</Tag>
                      <ReactECharts option={getChartPreview(c)} style={{ height: 250, marginTop: 12 }} />
                    </Card>
                  </Col>
                ))}
              </Row>
            )
          )}
        </Spin>
      </div>

      {/* 新建仪表盘 */}
      <Modal title="新建仪表盘" open={dashModalOpen} onCancel={() => setDashModalOpen(false)} onOk={() => dashForm.submit()} okText="创建">
        <Form form={dashForm} onFinish={createDashboard} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="is_public" label="是否公开" initialValue={true}>
            <Select>
              <Select.Option value={true}>公开</Select.Option>
              <Select.Option value={false}>私有</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 新建图表 */}
      <Modal title="新建图表" open={chartModalOpen} onCancel={() => setChartModalOpen(false)} onOk={() => chartForm.submit()} okText="创建">
        <Form form={chartForm} onFinish={createChart} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="chart_type" label="图表类型" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="bar">柱状图</Select.Option>
              <Select.Option value="line">折线图</Select.Option>
              <Select.Option value="pie">饼图</Select.Option>
              <Select.Option value="scatter">散点图</Select.Option>
              <Select.Option value="radar">雷达图</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="data_source" label="数据来源"><Input placeholder="数据来源" /></Form.Item>
          <Form.Item name="config" label="配置 (JSON)"><Input.TextArea rows={3} placeholder='{"key": "value"}' /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
