import { useState, useEffect, useCallback } from 'react'
import { Row, Col, Card, Statistic, Spin, Input, message, Empty, Modal, List, Tag, Button, Popconfirm } from 'antd'
import {
  BarChartOutlined, TeamOutlined, RiseOutlined, BankOutlined,
  SearchOutlined, HeartOutlined, HeartFilled, EyeOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { statisticsAPI, positionAPI } from '../../api'

function toArray(data) {
  if (!data) return []
  if (Array.isArray(data)) return data
  if (typeof data === 'object') return Object.entries(data).map(([name, value]) => ({ name, value }))
  return []
}

export default function Statistics() {
  const [keyword, setKeyword] = useState('')
  const [scope, setScope] = useState('all') // 'all' | 'favorites'
  const [basic, setBasic] = useState(null)
  const [salary, setSalary] = useState([])
  const [experience, setExperience] = useState([])
  const [education, setEducation] = useState([])
  const [city, setCity] = useState([])
  const [industry, setIndustry] = useState([])
  const [company, setCompany] = useState([])
  const [loading, setLoading] = useState(true)
  // 收藏岗位弹窗
  const [favModalOpen, setFavModalOpen] = useState(false)
  const [favList, setFavList] = useState([])
  const [favLoading, setFavLoading] = useState(false)
  // 岗位详情弹窗
  const [detailModal, setDetailModal] = useState({ open: false, item: null })

  const loadAll = useCallback(async () => {
    setLoading(true)
    const params = {}
    if (keyword.trim()) params.keyword = keyword.trim()
    if (scope === 'favorites') params.scope = 'favorites'

    try {
      const [b, s, exp, edu, c, ind, comp] = await Promise.allSettled([
        statisticsAPI.basic(params),
        statisticsAPI.salaryDist(params),
        statisticsAPI.expDist(params),
        statisticsAPI.eduDist(params),
        statisticsAPI.cityDist(params),
        statisticsAPI.industryDist(params),
        statisticsAPI.companyDist(params),
      ])
      if (b.status === 'fulfilled') setBasic(b.value.data)
      if (s.status === 'fulfilled') setSalary(toArray(s.value.data))
      if (exp.status === 'fulfilled') setExperience(toArray(exp.value.data))
      if (edu.status === 'fulfilled') setEducation(toArray(edu.value.data))
      if (c.status === 'fulfilled') setCity(toArray(c.value.data))
      if (ind.status === 'fulfilled') setIndustry(toArray(ind.value.data))
      if (comp.status === 'fulfilled') setCompany(toArray(comp.value.data))
    } catch {
      message.error('加载统计数据失败')
    } finally {
      setLoading(false)
    }
  }, [keyword, scope])

  useEffect(() => { loadAll() }, [scope])

  const handleSearch = () => loadAll()

  // 打开收藏岗位弹窗
  const openFavModal = async () => {
    setFavModalOpen(true)
    setFavLoading(true)
    try {
      const { data } = await positionAPI.favorites({ page_size: 200 })
      setFavList(data.results || data || [])
    } catch {
      message.error('加载收藏岗位失败')
    } finally {
      setFavLoading(false)
    }
  }

  // 取消收藏
  const handleUnfavorite = async (id) => {
    try {
      await positionAPI.unfavorite(id)
      message.success('已取消收藏')
      setFavList((prev) => prev.filter((p) => p.id !== id))
      // 刷新统计
      loadAll()
    } catch {
      message.error('取消收藏失败')
    }
  }

  const barOption = (title, data, color = '#00bebd') => ({
    title: { text: title, left: 'center', textStyle: { fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'axis', formatter: '{b}<br/>{c} 个职位' },
    xAxis: { type: 'category', data: data.map((d) => d.name), axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: '数量' },
    series: [{ data: data.map((d) => d.value), type: 'bar', itemStyle: { color, borderRadius: [6, 6, 0, 0] }, barMaxWidth: 50 }],
    grid: { left: '10%', right: '5%', bottom: '20%', top: '15%' },
  })

  const pieOption = (title, data) => ({
    title: { text: title, left: 'center', textStyle: { fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, type: 'scroll' },
    color: ['#00bebd', '#1890ff', '#722ed1', '#fe574a', '#fa8c16', '#52c41a', '#eb2f96', '#faad14', '#13c2c2', '#2f54eb'],
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
      label: { formatter: '{b}\n{d}%', fontSize: 11 },
      data: data.map((d) => ({ name: d.name, value: d.value })),
    }],
  })

  const chartOrEmpty = (data, option, height = 350) =>
    data.length > 0
      ? <ReactECharts option={option} style={{ height }} />
      : <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>暂无数据</div>

  return (
    <div className="page-container">
      <h2 className="section-title">
        <BarChartOutlined style={{ color: '#00bebd', marginRight: 8 }} />统计分析与可视化
      </h2>

      {/* 搜索 + Tab 切换 */}
      <div className="filter-panel" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={14}>
            <Input
              size="large"
              placeholder="输入职位关键词进行统计分析，如 Python、产品经理、数据分析..."
              prefix={<SearchOutlined style={{ color: '#00bebd' }} />}
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col xs={24} sm={10}>
            <div className="category-tabs" style={{ border: 'none', margin: 0 }}>
              <div className={`category-tab ${scope === 'all' ? 'active' : ''}`} onClick={() => setScope('all')}>
                <SearchOutlined style={{ marginRight: 4 }} />全部职位
              </div>
              <div className={`category-tab ${scope === 'favorites' ? 'active' : ''}`} onClick={() => setScope('favorites')}>
                <HeartOutlined style={{ marginRight: 4 }} />意向岗位
              </div>
            </div>
          </Col>
        </Row>
        {keyword && (
          <div style={{ marginTop: 8, color: '#666', fontSize: 13 }}>
            当前筛选：<span style={{ color: '#00bebd', fontWeight: 600 }}>「{keyword}」</span>
            {scope === 'favorites' && <span style={{ marginLeft: 8, color: '#eb2f96' }}>仅意向岗位</span>}
          </div>
        )}
      </div>

      <Spin spinning={loading}>
        {/* 概览卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={12} md={6}>
            <Card hoverable onClick={openFavModal} style={{ cursor: 'pointer' }}>
              <Statistic title="职位总数（点击查看收藏）" value={basic?.total_positions || 0} prefix={<BarChartOutlined />} valueStyle={{ color: '#00bebd' }} />
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card><Statistic title="平均薪资" value={basic?.avg_salary || 0} suffix="K" prefix={<RiseOutlined />} valueStyle={{ color: '#fe574a' }} precision={1} /></Card>
          </Col>
          <Col xs={12} md={6}>
            <Card><Statistic title="相关公司" value={basic?.total_companies || 0} prefix={<BankOutlined />} valueStyle={{ color: '#722ed1' }} /></Card>
          </Col>
          <Col xs={12} md={6}>
            <Card><Statistic title="覆盖城市" value={basic?.total_cities || 0} prefix={<TeamOutlined />} valueStyle={{ color: '#1890ff' }} /></Card>
          </Col>
        </Row>

        {basic?.total_positions === 0 && scope === 'favorites' ? (
          <Empty description="暂无意向岗位，请先在职位页面收藏岗位" style={{ padding: 60 }} />
        ) : (
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card>{chartOrEmpty(salary, barOption('薪资分布', salary))}</Card>
            </Col>
            <Col xs={24} md={12}>
              <Card>{chartOrEmpty(education, pieOption('学历要求分布', education))}</Card>
            </Col>
            <Col xs={24} md={12}>
              <Card>{chartOrEmpty(experience, barOption('经验要求分布', experience, '#722ed1'))}</Card>
            </Col>
            <Col xs={24} md={12}>
              <Card>{chartOrEmpty(industry, pieOption('行业分布', industry))}</Card>
            </Col>
            <Col xs={24} md={12}>
              <Card>{chartOrEmpty(city, barOption('城市分布 Top10', city, '#1890ff'))}</Card>
            </Col>
            <Col xs={24} md={12}>
              <Card>{chartOrEmpty(company, barOption('热门公司 Top10', company, '#fa8c16'))}</Card>
            </Col>
          </Row>
        )}
      </Spin>

      {/* 收藏岗位弹窗 */}
      <Modal
        title={<><HeartFilled style={{ color: '#ff4d4f', marginRight: 8 }} />我的收藏岗位</>}
        open={favModalOpen}
        onCancel={() => setFavModalOpen(false)}
        footer={null}
        width={720}
      >
        <Spin spinning={favLoading}>
          {favList.length === 0 ? (
            <Empty description="暂无收藏岗位，请先在职位页面收藏" />
          ) : (
            <List
              dataSource={favList}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button type="link" icon={<EyeOutlined />} onClick={() => setDetailModal({ open: true, item })}>查看</Button>,
                    <Popconfirm title="确认取消收藏？" onConfirm={() => handleUnfavorite(item.id)}>
                      <Button type="link" danger icon={<HeartFilled />}>取消收藏</Button>
                    </Popconfirm>,
                  ]}
                >
                  <List.Item.Meta
                    title={<span style={{ fontWeight: 600 }}>{item.title} <Tag color="red">{item.salary_range}</Tag></span>}
                    description={<span>{item.company} · {item.location} · {item.experience} · {item.education}</span>}
                  />
                </List.Item>
              )}
            />
          )}
        </Spin>
      </Modal>

      {/* 岗位详情弹窗 */}
      <Modal
        title={detailModal.item?.title}
        open={detailModal.open}
        onCancel={() => setDetailModal({ open: false, item: null })}
        footer={null}
        width={640}
      >
        {detailModal.item && (
          <div>
            <Row gutter={[16, 12]}>
              <Col span={12}><strong>公司：</strong>{detailModal.item.company}</Col>
              <Col span={12}><strong>薪资：</strong><span style={{ color: '#fe574a', fontWeight: 600 }}>{detailModal.item.salary_range}</span></Col>
              <Col span={12}><strong>城市：</strong>{detailModal.item.location}</Col>
              <Col span={12}><strong>经验：</strong>{detailModal.item.experience}</Col>
              <Col span={12}><strong>学历：</strong>{detailModal.item.education}</Col>
              <Col span={12}><strong>类型：</strong>{detailModal.item.position_type}</Col>
              <Col span={12}><strong>行业：</strong>{detailModal.item.industry}</Col>
              <Col span={24}><strong>福利：</strong>{detailModal.item.benefits}</Col>
            </Row>
            {detailModal.item.description && (
              <div style={{ marginTop: 16 }}>
                <strong>岗位描述：</strong>
                <div style={{ marginTop: 8, whiteSpace: 'pre-wrap', color: '#666', background: '#fafafa', padding: 12, borderRadius: 8 }}>
                  {detailModal.item.description}
                </div>
              </div>
            )}
            {detailModal.item.requirements && (
              <div style={{ marginTop: 16 }}>
                <strong>岗位要求：</strong>
                <div style={{ marginTop: 8, whiteSpace: 'pre-wrap', color: '#666', background: '#fafafa', padding: 12, borderRadius: 8 }}>
                  {detailModal.item.requirements}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
