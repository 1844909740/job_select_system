import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Input, Button, Row, Col, Tag, Spin } from 'antd'
import { SearchOutlined, FireOutlined, ThunderboltOutlined, GlobalOutlined, RocketOutlined } from '@ant-design/icons'
import { positionAPI } from '../../api'

const categories = ['互联网/AI', '电子/通信', '产品', '运营', '销售', '人力/行政', '财务/审计']
const hotTags = ['Python', '数据采集', '全栈工程师', '机器学习', '深度学习', '数据挖掘', 'Golang', 'Java']

const cities = [
  { name: '北京', en: 'Beijing', color: '#ff6b6b' },
  { name: '上海', en: 'Shanghai', color: '#4ecdc4' },
  { name: '广州', en: 'Guangzhou', color: '#45b7d1' },
  { name: '深圳', en: 'Shenzhen', color: '#96ceb4' },
  { name: '杭州', en: 'Hangzhou', color: '#ffeaa7' },
  { name: '成都', en: 'Chengdu', color: '#dfe6e9' },
  { name: '武汉', en: 'Wuhan', color: '#a29bfe' },
  { name: '西安', en: 'Xi\'an', color: '#fd79a8' },
]

const mockCompanies = [
  { name: '字节跳动', tag: 'D轮', size: '10000人以上', industry: '互联网', jobs: [{ title: 'Python开发工程师', salary: '25-50K' }, { title: '数据分析师', salary: '20-40K' }] },
  { name: '阿里巴巴', tag: '已上市', size: '10000人以上', industry: '互联网', jobs: [{ title: '全栈工程师', salary: '30-60K' }, { title: 'AI工程师', salary: '35-70K' }] },
  { name: '腾讯', tag: '已上市', size: '10000人以上', industry: '互联网', jobs: [{ title: '后端开发', salary: '25-50K' }, { title: '产品经理', salary: '20-40K' }] },
]

export default function Home() {
  const navigate = useNavigate()
  const [keyword, setKeyword] = useState('')
  const [activeCategory, setActiveCategory] = useState(0)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    setLoading(true)
    try {
      const { data } = await positionAPI.list({ page: 1 })
      setJobs(data.results || [])
    } catch {
      // 使用模拟数据
      setJobs(generateMockJobs())
    } finally {
      setLoading(false)
    }
  }

  const generateMockJobs = () => [
    { id: 1, title: 'Python高级开发工程师', salary_range: '15-25K', company: '科技有限公司', location: '北京', experience: '3-5年', education: '本科', industry: '互联网', position_type: '全职' },
    { id: 2, title: '数据分析师', salary_range: '12-20K', company: '数据科技公司', location: '上海', experience: '1-3年', education: '本科', industry: '互联网', position_type: '全职' },
    { id: 3, title: '全栈开发工程师', salary_range: '20-35K', company: '创新科技', location: '深圳', experience: '3-5年', education: '本科', industry: '互联网', position_type: '全职' },
    { id: 4, title: 'AI工程师', salary_range: '25-45K', company: '人工智能研究院', location: '杭州', experience: '3-5年', education: '硕士', industry: '互联网', position_type: '全职' },
    { id: 5, title: '前端开发工程师', salary_range: '15-25K', company: '互联网公司', location: '广州', experience: '1-3年', education: '本科', industry: '互联网', position_type: '全职' },
    { id: 6, title: '产品经理', salary_range: '18-30K', company: '产品科技', location: '成都', experience: '3-5年', education: '本科', industry: '互联网', position_type: '全职' },
    { id: 7, title: '运维工程师', salary_range: '10-18K', company: '云服务公司', location: '武汉', experience: '1-3年', education: '大专', industry: '互联网', position_type: '全职' },
    { id: 8, title: '机器学习工程师', salary_range: '30-50K', company: 'AI科技', location: '北京', experience: '5-10年', education: '硕士', industry: '互联网', position_type: '全职' },
    { id: 9, title: '测试工程师', salary_range: '10-15K', company: '软件科技', location: '西安', experience: '1-3年', education: '本科', industry: '互联网', position_type: '全职' },
  ]

  const displayJobs = jobs.length > 0 ? jobs : generateMockJobs()

  const handleSearch = () => {
    navigate(`/position?keywords=${encodeURIComponent(keyword)}`)
  }

  return (
    <div>
      {/* 搜索栏 */}
      <div className="search-banner">
        <div className="search-bar-wrapper">
          <div className="search-bar">
            <Input
              placeholder="搜索职位、公司"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onPressEnter={handleSearch}
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>搜索</Button>
          </div>
          <div className="hot-tags">
            <span>热门职位：</span>
            {hotTags.map((tag) => (
              <a key={tag} onClick={() => navigate(`/position?keywords=${tag}`)}>{tag}</a>
            ))}
          </div>
        </div>
      </div>

      <div className="page-container">
        {/* 精选职位 */}
        <h2 className="section-title"><FireOutlined style={{ color: '#ff6b6b', marginRight: 8 }} />精选职位</h2>

        <Spin spinning={loading}>
          <Row gutter={[16, 16]}>
            {displayJobs.slice(0, 9).map((job) => (
              <Col xs={24} sm={12} md={8} key={job.id}>
                <div className="job-card" onClick={() => navigate('/position')}>
                  <div className="job-card-header">
                    <div className="job-card-title">{job.title}</div>
                    <div className="job-card-salary">{job.salary_range}</div>
                  </div>
                  <div className="job-card-tags">
                    {job.experience && <Tag>{job.experience}</Tag>}
                    {job.education && <Tag>{job.education}</Tag>}
                    {job.position_type && <Tag>{job.position_type}</Tag>}
                  </div>
                  <div className="job-card-company">
                    <span>{job.company}</span>
                  </div>
                  <div className="job-card-location">{job.location} · {job.industry}</div>
                </div>
              </Col>
            ))}
          </Row>
        </Spin>

        {/* 热招职位 */}
        <h2 className="section-title" style={{ marginTop: 48 }}>
          <ThunderboltOutlined style={{ color: '#ffa940', marginRight: 8 }} />热招职位
        </h2>
        <div className="category-tabs">
          {categories.map((cat, idx) => (
            <div key={cat} className={`category-tab ${idx === activeCategory ? 'active' : ''}`}
              onClick={() => setActiveCategory(idx)}>
              {cat}
            </div>
          ))}
        </div>
        <Row gutter={[16, 16]}>
          {displayJobs.slice(0, 6).map((job) => (
            <Col xs={24} sm={12} md={8} key={`hot-${job.id}`}>
              <div className="job-card" onClick={() => navigate('/position')}>
                <div className="job-card-header">
                  <div className="job-card-title">{job.title}</div>
                  <div className="job-card-salary">{job.salary_range}</div>
                </div>
                <div className="job-card-tags">
                  {job.location && <Tag color="blue">{job.location}</Tag>}
                  {job.experience && <Tag>{job.experience}</Tag>}
                  {job.education && <Tag>{job.education}</Tag>}
                </div>
                <div className="job-card-company"><span>{job.company}</span></div>
              </div>
            </Col>
          ))}
        </Row>

        {/* 热门企业 */}
        <h2 className="section-title" style={{ marginTop: 48 }}>
          <RocketOutlined style={{ color: '#722ed1', marginRight: 8 }} />热门企业
        </h2>
        <Row gutter={[16, 16]}>
          {mockCompanies.map((company) => (
            <Col xs={24} sm={12} md={8} key={company.name}>
              <div className="company-card">
                <div className="company-header">
                  <div className="company-logo">{company.name[0]}</div>
                  <div className="company-info">
                    <h4>{company.name}</h4>
                    <span>{company.tag} · {company.size} · {company.industry}</span>
                  </div>
                </div>
                <div className="company-jobs">
                  {company.jobs.map((job, idx) => (
                    <div className="company-job-item" key={idx}>
                      <span className="title">{job.title}</span>
                      <span className="salary">{job.salary}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Col>
          ))}
        </Row>

        {/* 城市热招 */}
        <h2 className="section-title" style={{ marginTop: 48 }}>
          <GlobalOutlined style={{ color: '#1890ff', marginRight: 8 }} />城市热招
        </h2>
        <Row gutter={[16, 16]}>
          {cities.map((city) => (
            <Col xs={12} sm={8} md={6} key={city.name}>
              <div className="city-card" onClick={() => navigate(`/position?location=${city.name}`)}>
                <div style={{
                  width: '100%', height: '100%',
                  background: `linear-gradient(135deg, ${city.color}, ${city.color}88)`,
                }} />
                <div className="city-card-overlay">
                  <div className="city-card-name">{city.name}</div>
                  <div className="city-card-en">{city.en}</div>
                </div>
              </div>
            </Col>
          ))}
        </Row>
      </div>
    </div>
  )
}
