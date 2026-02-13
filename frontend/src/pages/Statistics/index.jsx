import { useState, useEffect, useCallback } from 'react'
import { Row, Col, Card, Statistic, Spin, Input, message, Empty, Modal, List, Tag, Button, Descriptions } from 'antd'
import {
  BarChartOutlined, TeamOutlined, RiseOutlined, BankOutlined,
  SearchOutlined, HeartOutlined, HeartFilled, DeleteOutlined,
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
  const [favModalOpen, setFavModalOpen] = useState(false)
  const [favorites, setFavorites] = useState([])
  const [favLoading, setFavLoading] = useState(false)
  const [positionDetail, setPositionDetail] = useState(null)

  const loadFavorites = async () => {
    setFavLoading(true)
    try {
      const { data } = await positionAPI.favorites()
      setFavorites(data.results || data || [])
    } catch {
      message.error('加载收藏岗位失败')
    } finally {
      setFavLoading(false)
    }
  }

  const handleUnfavorite = async (positionId) => {
    try {
      await positionAPI.unfavorite(positionId)
      message.success('已取消收藏')
      setFavorites((prev) => prev.filter((f) => (f.position_detail?.id || f.position?.id || f.position) !== positionId))
    } catch {
      message.error('取消收藏失败')
    }
  }

  const openFavModal = () => {
    setFavModalOpen(true)
    loadFavorites()
  }

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
              <Statistic title="职位总数" value={basic?.total_positions || 0} prefix={<BarChartOutlined />} valueStyle={{ color: '#00bebd' }} />
              <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>点击查看收藏岗位</div>
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
        width={750}
      >
        <Spin spinning={favLoading}>
          {favorites.length === 0 ? (
            <Empty description="暂无收藏岗位，请先在职位页面收藏岗位" style={{ padding: 40 }} />
          ) : (
            <List
              dataSource={favorites}
              renderItem={(fav) => {
                const pos = fav.position_detail || fav.position || {}
                const posId = pos.id || fav.position
                return (
                  <List.Item
                    actions={[
                      <Button
                        key="unfav"
                        type="link"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleUnfavorite(posId)}
                      >
                        取消收藏
                      </Button>,
                    ]}
                  >
                    <List.Item.Meta
                      title={
                        <a onClick={() => setPositionDetail(pos)} style={{ color: '#333' }}>
                          {pos.title || '未知岗位'} <Tag color="red">{pos.salary_range}</Tag>
                        </a>
                      }
                      description={
                        <span>
                          {pos.company} · {pos.location}
                          {pos.experience && ` · ${pos.experience}`}
                          {pos.education && ` · ${pos.education}`}
                        </span>
                      }
                    />
                  </List.Item>
                )
              }}
            />
          )}
        </Spin>
      </Modal>

      {/* 岗位详情弹窗 */}
      <Modal
        open={!!positionDetail}
        onCancel={() => setPositionDetail(null)}
        footer={null}
        width={700}
        title={positionDetail?.title}
      >
        {positionDetail && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="薪资范围"><span style={{ color: '#fe574a', fontWeight: 600 }}>{positionDetail.salary_range}</span></Descriptions.Item>
            <Descriptions.Item label="工作城市">{positionDetail.location}</Descriptions.Item>
            <Descriptions.Item label="经验要求">{positionDetail.experience}</Descriptions.Item>
            <Descriptions.Item label="学历要求">{positionDetail.education}</Descriptions.Item>
            <Descriptions.Item label="职位类型">{positionDetail.position_type}</Descriptions.Item>
            <Descriptions.Item label="所属行业">{positionDetail.industry}</Descriptions.Item>
            <Descriptions.Item label="公司名称" span={2}>{positionDetail.company}</Descriptions.Item>
            {positionDetail.description && <Descriptions.Item label="职位描述" span={2}>{positionDetail.description}</Descriptions.Item>}
            {positionDetail.requirements && <Descriptions.Item label="职位要求" span={2}>{positionDetail.requirements}</Descriptions.Item>}
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}
