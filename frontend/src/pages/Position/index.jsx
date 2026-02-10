import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Input, Select, Row, Col, Tag, Pagination, Spin, Button, Modal, Descriptions, message, Empty } from 'antd'
import { SearchOutlined, HeartOutlined, HeartFilled, EnvironmentOutlined, MoneyCollectOutlined } from '@ant-design/icons'
import { positionAPI } from '../../api'

const experienceOptions = ['不限', '应届', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
const educationOptions = ['不限', '大专', '本科', '硕士', '博士']
const salaryOptions = ['不限', '5K以下', '5-10K', '10-15K', '15-20K', '20-30K', '30-50K', '50K以上']

export default function Position() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [keyword, setKeyword] = useState(searchParams.get('keywords') || '')
  const [location, setLocation] = useState(searchParams.get('location') || '')
  const [experience, setExperience] = useState('不限')
  const [education, setEducation] = useState('不限')
  const [salary, setSalary] = useState('不限')
  const [jobs, setJobs] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState(null)
  const [favorites, setFavorites] = useState(new Set())

  useEffect(() => {
    fetchJobs()
  }, [page])

  const fetchJobs = async () => {
    setLoading(true)
    try {
      const params = { page }
      if (keyword) params.keywords = keyword
      if (location && location !== '不限') params.location = location
      if (experience !== '不限') params.experience = experience
      if (education !== '不限') params.education = education
      const { data } = await positionAPI.list(params)
      setJobs(data.results || [])
      setTotal(data.count || 0)
    } catch {
      setJobs([])
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(1)
    fetchJobs()
  }

  const handleFavorite = async (e, jobId) => {
    e.stopPropagation()
    try {
      if (favorites.has(jobId)) {
        await positionAPI.unfavorite(jobId)
        setFavorites((prev) => { const s = new Set(prev); s.delete(jobId); return s })
        message.success('已取消收藏')
      } else {
        await positionAPI.favorite(jobId)
        setFavorites((prev) => new Set(prev).add(jobId))
        message.success('已收藏')
      }
    } catch {
      message.error('操作失败，请先登录')
    }
  }

  const showDetail = async (job) => {
    try {
      const { data } = await positionAPI.get(job.id)
      setDetail(data)
    } catch {
      setDetail(job)
    }
  }

  return (
    <div className="page-container">
      {/* 筛选面板 */}
      <div className="filter-panel">
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={10}>
            <Input
              size="large"
              placeholder="搜索职位、公司关键词"
              prefix={<SearchOutlined style={{ color: '#00bebd' }} />}
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col xs={12} sm={4}>
            <Input size="large" placeholder="城市" prefix={<EnvironmentOutlined />}
              value={location} onChange={(e) => setLocation(e.target.value)} />
          </Col>
          <Col xs={12} sm={3}>
            <Select size="large" value={experience} onChange={setExperience} style={{ width: '100%' }}>
              {experienceOptions.map((o) => <Select.Option key={o} value={o}>{o}</Select.Option>)}
            </Select>
          </Col>
          <Col xs={12} sm={3}>
            <Select size="large" value={education} onChange={setEducation} style={{ width: '100%' }}>
              {educationOptions.map((o) => <Select.Option key={o} value={o}>{o}</Select.Option>)}
            </Select>
          </Col>
          <Col xs={12} sm={4}>
            <Button type="primary" size="large" block icon={<SearchOutlined />} onClick={handleSearch}>搜索</Button>
          </Col>
        </Row>
      </div>

      {/* 职位列表 */}
      <Spin spinning={loading}>
        {jobs.length === 0 && !loading ? (
          <Empty description="暂无职位数据，请先通过数据采集添加数据" style={{ padding: 80 }} />
        ) : (
          <Row gutter={[16, 16]}>
            {jobs.map((job) => (
              <Col xs={24} sm={12} md={8} key={job.id}>
                <div className="job-card" onClick={() => showDetail(job)}>
                  <div className="job-card-header">
                    <div className="job-card-title">{job.title}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="job-card-salary">{job.salary_range}</span>
                      <span onClick={(e) => handleFavorite(e, job.id)} style={{ cursor: 'pointer', fontSize: 18 }}>
                        {favorites.has(job.id) ? <HeartFilled style={{ color: '#ff4d4f' }} /> : <HeartOutlined style={{ color: '#ccc' }} />}
                      </span>
                    </div>
                  </div>
                  <div className="job-card-tags">
                    {job.experience && <Tag>{job.experience}</Tag>}
                    {job.education && <Tag>{job.education}</Tag>}
                    {job.position_type && <Tag color="cyan">{job.position_type}</Tag>}
                  </div>
                  <div className="job-card-company">
                    <span>{job.company}</span>
                    {job.industry && <span>· {job.industry}</span>}
                  </div>
                  <div className="job-card-location">
                    <EnvironmentOutlined style={{ marginRight: 4 }} />{job.location}
                  </div>
                </div>
              </Col>
            ))}
          </Row>
        )}
      </Spin>

      {total > 0 && (
        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <Pagination current={page} total={total} pageSize={10} onChange={(p) => setPage(p)} showTotal={(t) => `共 ${t} 个职位`} />
        </div>
      )}

      {/* 详情弹窗 */}
      <Modal open={!!detail} onCancel={() => setDetail(null)} footer={null} width={700}
        title={detail?.title}>
        {detail && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="薪资范围"><span style={{ color: '#fe574a', fontWeight: 600 }}>{detail.salary_range}</span></Descriptions.Item>
            <Descriptions.Item label="工作城市">{detail.location}</Descriptions.Item>
            <Descriptions.Item label="经验要求">{detail.experience}</Descriptions.Item>
            <Descriptions.Item label="学历要求">{detail.education}</Descriptions.Item>
            <Descriptions.Item label="职位类型">{detail.position_type}</Descriptions.Item>
            <Descriptions.Item label="所属行业">{detail.industry}</Descriptions.Item>
            <Descriptions.Item label="公司名称" span={2}>{detail.company}</Descriptions.Item>
            {detail.description && <Descriptions.Item label="职位描述" span={2}>{detail.description}</Descriptions.Item>}
            {detail.requirements && <Descriptions.Item label="职位要求" span={2}>{detail.requirements}</Descriptions.Item>}
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}
