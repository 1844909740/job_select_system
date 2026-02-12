import { useState, useEffect } from 'react'
import {
  Card, Row, Col, Button, Select, Input, Upload, Tabs, Tag, Table,
  Space, message, Spin, Descriptions, Empty, Divider, List, Modal,
} from 'antd'
import {
  RobotOutlined, SearchOutlined, UploadOutlined, ExperimentOutlined,
  ThunderboltOutlined, FileTextOutlined, StarOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { aiAPI } from '../../api'

const ALGORITHMS = [
  { value: 'recommendation', label: '推荐算法', color: '#00bebd', desc: '基于协同过滤，为你推荐最匹配的岗位' },
  { value: 'prediction', label: '趋势预测', color: '#1890ff', desc: '预测岗位未来需求与薪资趋势' },
  { value: 'classification', label: '职位分类', color: '#722ed1', desc: '按行业对相关岗位进行智能分类' },
  { value: 'clustering', label: '聚类分析', color: '#52c41a', desc: '将岗位按特征聚类为不同群组' },
  { value: 'sentiment', label: '情感分析', color: '#fa8c16', desc: '分析岗位描述的正面/负面情感倾向' },
  { value: 'nlp', label: '自然语言处理', color: '#eb2f96', desc: '从岗位要求中提取关键技能词汇' },
]

export default function AIAnalysis() {
  const [algorithm, setAlgorithm] = useState('recommendation')
  const [keyword, setKeyword] = useState('')
  const [resumeText, setResumeText] = useState('')
  const [manualSkills, setManualSkills] = useState('')
  const [fileList, setFileList] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('search')
  const [tasks, setTasks] = useState([])
  const [positionDetailModal, setPositionDetailModal] = useState(false)
  const [selectedPosition, setSelectedPosition] = useState(null)

  useEffect(() => { loadTasks() }, [])

  const loadTasks = async () => {
    try {
      const { data } = await aiAPI.tasks.list()
      setTasks((data.results || data || []).slice(0, 10))
    } catch {}
  }

  // ====== 职位搜索分析 ======
  const handleSearchAnalysis = async () => {
    if (!keyword.trim()) return message.warning('请输入职位关键词')
    setLoading(true)
    setResult(null)
    try {
      const { data } = await aiAPI.tasks.create({
        title: `${keyword} - ${ALGORITHMS.find(a => a.value === algorithm)?.label}`,
        algorithm_type: algorithm,
        input_data: { keyword: keyword.trim() },
        parameters: { source: 'search', keyword: keyword.trim() },
      })
      // 执行任务
      const execRes = await aiAPI.tasks.execute(data.id)
      setResult(execRes.data.result)
      message.success('分析完成')
      loadTasks()
    } catch (err) {
      message.error('分析失败：' + (err.response?.data?.message || '请稍后重试'))
    } finally {
      setLoading(false)
    }
  }

  // ====== 简历分析 ======
  const handleResumeAnalysis = async () => {
    if (!resumeText.trim() && fileList.length === 0 && !manualSkills.trim()) {
      return message.warning('请粘贴简历内容、上传简历文件或输入技能关键词')
    }
    setLoading(true)
    setResult(null)
    try {
      let payload
      if (fileList.length > 0 && fileList[0].originFileObj) {
        payload = new FormData()
        payload.append('resume_file', fileList[0].originFileObj)
        payload.append('algorithm_type', algorithm)
        if (manualSkills.trim()) {
          payload.append('manual_skills', manualSkills.trim())
        }
      } else {
        payload = { 
          resume_text: resumeText.trim(), 
          algorithm_type: algorithm,
          manual_skills: manualSkills.trim()
        }
      }
      const { data } = await aiAPI.analyzeResume(payload)
      setResult(data)
      message.success('简历分析完成')
      loadTasks()
    } catch (err) {
      message.error('分析失败：' + (err.response?.data?.error || '请稍后重试'))
    } finally {
      setLoading(false)
    }
  }

  // ====== 查看岗位详情 ======
  const showPositionDetail = async (positionId) => {
    try {
      const { data } = await aiAPI.getPositionDetail(positionId)
      setSelectedPosition(data)
      setPositionDetailModal(true)
    } catch (err) {
      message.error('获取岗位详情失败：' + (err.response?.data?.error || '请稍后重试'))
    }
  }

  const algoInfo = ALGORITHMS.find((a) => a.value === algorithm)

  // ====== 结果可视化 ======
  const renderResult = () => {
    if (!result) return null

    return (
      <div style={{ marginTop: 24 }}>
        <Card title={<><ExperimentOutlined style={{ marginRight: 8, color: algoInfo?.color }} />{result.algorithm || '分析结果'}</>}
          extra={<Tag color={algoInfo?.color}>{result.total_analyzed ?? result.total_matched ?? 0} 条数据分析</Tag>}>

          <p style={{ color: '#666', marginBottom: 16 }}>{result.description}</p>

          {/* 提取的关键词 */}
          {result.extracted_keywords && (
            <div style={{ marginBottom: 16 }}>
              <strong>提取的技能关键词：</strong>
              {result.extracted_keywords.map((k) => <Tag key={k} color="cyan" style={{ margin: '2px 4px' }}>{k}</Tag>)}
            </div>
          )}

          {/* 推荐列表 */}
          {result.recommendations && (
            <>
              <Divider orientation="left">推荐岗位</Divider>
              <List
                dataSource={result.recommendations}
                renderItem={(item, idx) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<div style={{ width: 36, height: 36, borderRadius: '50%', background: '#00bebd', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>{idx + 1}</div>}
                      title={<span>{item.title} <Tag color="red">{item.salary}</Tag></span>}
                      description={<span>{item.company} · {item.location} {item.experience && `· ${item.experience}`}</span>}
                    />
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 20, fontWeight: 700, color: '#00bebd' }}>{(item.score * 100).toFixed(0)}%</div>
                      <div style={{ fontSize: 12, color: '#999' }}>匹配度</div>
                    </div>
                  </List.Item>
                )}
              />
            </>
          )}

          {/* 趋势预测图 */}
          {result.demand_trend && (
            <Row gutter={[16, 16]}>
              <Col xs={24} md={12}>
                <ReactECharts style={{ height: 300 }} option={{
                  title: { text: '需求量趋势预测', left: 'center', textStyle: { fontSize: 14 } },
                  tooltip: { trigger: 'axis' },
                  xAxis: { type: 'category', data: result.demand_trend.map(d => d.month) },
                  yAxis: { type: 'value' },
                  series: [{ data: result.demand_trend.map(d => d.value), type: 'line', smooth: true, areaStyle: { color: 'rgba(0,190,189,0.15)' }, itemStyle: { color: '#00bebd' } }],
                }} />
              </Col>
              {result.salary_trend && (
                <Col xs={24} md={12}>
                  <ReactECharts style={{ height: 300 }} option={{
                    title: { text: '薪资趋势预测 (K)', left: 'center', textStyle: { fontSize: 14 } },
                    tooltip: { trigger: 'axis' },
                    xAxis: { type: 'category', data: result.salary_trend.map(d => d.month) },
                    yAxis: { type: 'value' },
                    series: [{ data: result.salary_trend.map(d => d.value), type: 'line', smooth: true, areaStyle: { color: 'rgba(254,87,74,0.15)' }, itemStyle: { color: '#fe574a' } }],
                  }} />
                </Col>
              )}
            </Row>
          )}

          {/* 分类饼图 */}
          {result.classification && (
            <ReactECharts style={{ height: 350 }} option={{
              title: { text: '行业分类分布', left: 'center', textStyle: { fontSize: 14 } },
              tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
              legend: { bottom: 0 },
              color: ['#00bebd', '#1890ff', '#722ed1', '#fe574a', '#fa8c16', '#52c41a', '#eb2f96', '#faad14'],
              series: [{ type: 'pie', radius: ['35%', '65%'], data: result.classification.map(c => ({ name: c.name, value: c.value })) }],
            }} />
          )}

          {/* 聚类 */}
          {result.clusters && (
            <>
              <Divider orientation="left">聚类结果</Divider>
              <Row gutter={[16, 16]}>
                {result.clusters.map((c, i) => (
                  <Col xs={24} sm={8} key={i}>
                    <Card 
                      size="small" 
                      style={{ borderTop: `3px solid ${['#00bebd', '#1890ff', '#fa8c16'][i]}` }}
                      title={
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span>{c.name}</span>
                          <Tag color={['cyan', 'blue', 'orange'][i]}>{c.size} 个岗位</Tag>
                        </div>
                      }
                    >
                      <Descriptions column={1} size="small">
                        <Descriptions.Item label="平均薪资">{c.avg_salary}K</Descriptions.Item>
                        {c.features && <Descriptions.Item label="特征">{c.features}</Descriptions.Item>}
                      </Descriptions>
                      
                      {/* 显示该聚类下的岗位列表 */}
                      {c.positions && c.positions.length > 0 && (
                        <div style={{ marginTop: 12 }}>
                          <Divider style={{ margin: '8px 0' }}>匹配岗位</Divider>
                          <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                            {c.positions.slice(0, 5).map((pos, idx) => (
                              <div key={pos.id} style={{ 
                                padding: '8px 0', 
                                borderBottom: idx < 4 ? '1px solid #f0f0f0' : 'none',
                                cursor: 'pointer'
                              }} onClick={() => showPositionDetail(pos.id)}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                  <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 500, fontSize: 13, color: '#1890ff' }}>{pos.title}</div>
                                    <div style={{ fontSize: 12, color: '#666', marginTop: 2 }}>
                                      {pos.company} · {pos.location}
                                    </div>
                                    <div style={{ fontSize: 12, color: '#999', marginTop: 2 }}>
                                      {pos.salary} · {pos.experience}
                                    </div>
                                    {pos.matched_skills && pos.matched_skills.length > 0 && (
                                      <div style={{ marginTop: 4 }}>
                                        {pos.matched_skills.map(skill => (
                                          <Tag key={skill} size="small" color="green" style={{ fontSize: 10, margin: '1px' }}>
                                            {skill}
                                          </Tag>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                  <div style={{ textAlign: 'right', marginLeft: 8 }}>
                                    <div style={{ fontSize: 12, fontWeight: 600, color: ['#00bebd', '#1890ff', '#fa8c16'][i] }}>
                                      {pos.match_score}%
                                    </div>
                                    <div style={{ fontSize: 10, color: '#999' }}>匹配度</div>
                                  </div>
                                </div>
                              </div>
                            ))}
                            {c.positions.length > 5 && (
                              <div style={{ textAlign: 'center', padding: '8px 0', color: '#999', fontSize: 12 }}>
                                还有 {c.positions.length - 5} 个岗位...
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </Card>
                  </Col>
                ))}
              </Row>
              {result.scatter && (
                <ReactECharts style={{ height: 350, marginTop: 16 }} option={{
                  title: { text: '经验-薪资散点分布', left: 'center', textStyle: { fontSize: 14 } },
                  tooltip: { formatter: p => `经验: ${p.value[0]}年<br/>薪资: ${p.value[1]}K` },
                  xAxis: { name: '经验(年)', type: 'value' },
                  yAxis: { name: '薪资(K)', type: 'value' },
                  series: [{ type: 'scatter', symbolSize: 8, data: result.scatter, itemStyle: { color: '#00bebd', opacity: 0.6 } }],
                }} />
              )}
            </>
          )}

          {/* 情感分析 */}
          {result.sentiment && (
            <Row gutter={[16, 16]}>
              <Col xs={24} md={12}>
                <ReactECharts style={{ height: 300 }} option={{
                  title: { text: '情感分布', left: 'center', textStyle: { fontSize: 14 } },
                  tooltip: { trigger: 'item' },
                  color: ['#52c41a', '#ff4d4f', '#d9d9d9'],
                  series: [{
                    type: 'pie', radius: ['40%', '70%'],
                    data: [
                      { name: '正面', value: result.sentiment.positive },
                      { name: '负面', value: result.sentiment.negative },
                      { name: '中性', value: result.sentiment.neutral },
                    ],
                  }],
                }} />
              </Col>
              {result.word_cloud && result.word_cloud.length > 0 && (
                <Col xs={24} md={12}>
                  <ReactECharts style={{ height: 300 }} option={{
                    title: { text: '高频词汇', left: 'center', textStyle: { fontSize: 14 } },
                    tooltip: {},
                    xAxis: { type: 'category', data: result.word_cloud.map(w => w.name), axisLabel: { rotate: 45 } },
                    yAxis: { type: 'value' },
                    series: [{ type: 'bar', data: result.word_cloud.map(w => w.value), itemStyle: { color: '#fa8c16', borderRadius: [4, 4, 0, 0] } }],
                  }} />
                </Col>
              )}
            </Row>
          )}

          {/* NLP技能 */}
          {result.skills && (
            <>
              <Divider orientation="left">技能提取</Divider>
              <ReactECharts style={{ height: 350 }} option={{
                title: { text: '关键技能词频', left: 'center', textStyle: { fontSize: 14 } },
                tooltip: {},
                xAxis: { type: 'category', data: result.skills.map(s => s.name), axisLabel: { rotate: 45, fontSize: 11 } },
                yAxis: { type: 'value' },
                series: [{ type: 'bar', data: result.skills.map(s => s.value), itemStyle: { color: '#eb2f96', borderRadius: [4, 4, 0, 0] } }],
                grid: { bottom: '25%' },
              }} />
              {result.skill_categories && (
                <Row gutter={[8, 8]} style={{ marginTop: 16 }}>
                  {result.skill_categories.map((cat) => (
                    <Col key={cat.category}>
                      <Tag color="blue">{cat.category}：{cat.skills.join('、')}</Tag>
                    </Col>
                  ))}
                </Row>
              )}
            </>
          )}
        </Card>
      </div>
    )
  }

  return (
    <div className="page-container">
      <h2 className="section-title"><RobotOutlined style={{ color: '#00bebd', marginRight: 8 }} />AI智能分析</h2>

      {/* 算法选择 */}
      <div className="filter-panel" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
            <div style={{ fontSize: 13, color: '#999', marginBottom: 4 }}>选择分析算法</div>
            <Select
              size="large" value={algorithm} onChange={setAlgorithm} style={{ width: '100%' }}
              optionLabelProp="label"
            >
              {ALGORITHMS.map((a) => (
                <Select.Option key={a.value} value={a.value} label={a.label}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <ExperimentOutlined style={{ color: a.color }} />
                    <div>
                      <div style={{ fontWeight: 600 }}>{a.label}</div>
                      <div style={{ fontSize: 12, color: '#999' }}>{a.desc}</div>
                    </div>
                  </div>
                </Select.Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={16}>
            <div style={{ background: `${algoInfo?.color}10`, border: `1px solid ${algoInfo?.color}30`, borderRadius: 8, padding: '12px 16px' }}>
              <ExperimentOutlined style={{ color: algoInfo?.color, marginRight: 8 }} />
              <strong style={{ color: algoInfo?.color }}>{algoInfo?.label}</strong>：{algoInfo?.desc}
            </div>
          </Col>
        </Row>
      </div>

      {/* 分析方式选择 */}
      <div className="table-card">
        <div className="category-tabs" style={{ marginBottom: 0 }}>
          <div className={`category-tab ${activeTab === 'search' ? 'active' : ''}`} onClick={() => setActiveTab('search')}>
            <SearchOutlined style={{ marginRight: 4 }} />搜索职位分析
          </div>
          <div className={`category-tab ${activeTab === 'resume' ? 'active' : ''}`} onClick={() => setActiveTab('resume')}>
            <FileTextOutlined style={{ marginRight: 4 }} />上传简历分析
          </div>
        </div>

        <div style={{ padding: '24px 0' }}>
          {activeTab === 'search' ? (
            <Row gutter={[16, 16]} align="middle">
              <Col xs={24} sm={18}>
                <Input
                  size="large"
                  placeholder="输入职位关键词，如 Python开发、数据分析师、产品经理..."
                  prefix={<SearchOutlined style={{ color: '#00bebd' }} />}
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  onPressEnter={handleSearchAnalysis}
                  allowClear
                />
              </Col>
              <Col xs={24} sm={6}>
                <Button type="primary" size="large" block icon={<ThunderboltOutlined />}
                  onClick={handleSearchAnalysis} loading={loading}>
                  开始分析
                </Button>
              </Col>
            </Row>
          ) : (
            <div>
              <Row gutter={[16, 16]}>
                <Col xs={24}>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 13, color: '#999', marginBottom: 4 }}>输入技能关键词（用逗号分隔）</div>
                    <Input
                      size="large"
                      placeholder="例如：Python, Django, React, MySQL, Redis, 机器学习, 数据分析..."
                      value={manualSkills}
                      onChange={(e) => setManualSkills(e.target.value)}
                      allowClear
                    />
                    <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                      💡 提示：可以直接输入技能进行聚类分析，或结合简历内容获得更精准的分析结果
                    </div>
                  </div>
                </Col>
              </Row>
              <Row gutter={[16, 16]}>
                <Col xs={24} md={16}>
                  <div style={{ fontSize: 13, color: '#999', marginBottom: 4 }}>简历内容（可选）</div>
                  <Input.TextArea
                    rows={8}
                    placeholder="粘贴你的简历内容...&#10;&#10;例如：&#10;姓名：张三&#10;技能：Python, Django, React, MySQL, Redis&#10;经验：3年后端开发经验&#10;学历：本科 计算机科学&#10;项目经历：负责过电商系统开发..."
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                  />
                </Col>
                <Col xs={24} md={8}>
                  <div style={{ fontSize: 13, color: '#999', marginBottom: 4 }}>或上传简历文件</div>
                  <div style={{ border: '2px dashed #d9d9d9', borderRadius: 12, padding: 24, textAlign: 'center', minHeight: 200, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <Upload
                      accept=".txt,.doc,.docx,.pdf"
                      maxCount={1}
                      fileList={fileList}
                      onChange={({ fileList }) => setFileList(fileList)}
                      beforeUpload={() => false}
                    >
                      <Button icon={<UploadOutlined />} size="large">上传简历文件</Button>
                    </Upload>
                    <p style={{ color: '#999', fontSize: 12, marginTop: 12 }}>支持 .txt / .doc / .docx / .pdf</p>
                  </div>
                </Col>
              </Row>
              <div style={{ marginTop: 16, textAlign: 'right' }}>
                <Button type="primary" size="large" icon={<ThunderboltOutlined />}
                  onClick={handleResumeAnalysis} loading={loading}>
                  分析简历匹配岗位
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 分析结果 */}
      <Spin spinning={loading}>
        {renderResult()}
      </Spin>

      {/* 历史任务 */}
      {tasks.length > 0 && (
        <Card title="最近分析记录" style={{ marginTop: 24 }} size="small">
          <Table
            dataSource={tasks} rowKey="id" size="small" pagination={false}
            columns={[
              { title: '名称', dataIndex: 'title', ellipsis: true },
              { title: '算法', dataIndex: 'algorithm_type', render: (t) => { const a = ALGORITHMS.find(x => x.value === t); return <Tag color={a?.color}>{a?.label || t}</Tag> } },
              { title: '状态', dataIndex: 'status', render: (s) => <Tag color={s === '已完成' ? 'success' : s === '失败' ? 'error' : 'processing'}>{s}</Tag> },
              { title: '时间', dataIndex: 'created_at', render: (t) => t?.slice(0, 16).replace('T', ' ') },
            ]}
          />
        </Card>
      )}

      {/* 岗位详情模态框 */}
      <Modal
        title="岗位详情"
        open={positionDetailModal}
        onCancel={() => setPositionDetailModal(false)}
        footer={[
          <Button key="close" onClick={() => setPositionDetailModal(false)}>
            关闭
          </Button>,
          selectedPosition?.source_url && (
            <Button key="visit" type="primary" onClick={() => window.open(selectedPosition.source_url, '_blank')}>
              查看原始页面
            </Button>
          )
        ]}
        width={800}
      >
        {selectedPosition && (
          <div>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="岗位名称" span={2}>
                <strong style={{ fontSize: 16, color: '#1890ff' }}>{selectedPosition.title}</strong>
              </Descriptions.Item>
              <Descriptions.Item label="公司">{selectedPosition.company}</Descriptions.Item>
              <Descriptions.Item label="地点">{selectedPosition.location}</Descriptions.Item>
              <Descriptions.Item label="薪资">{selectedPosition.salary_range}</Descriptions.Item>
              <Descriptions.Item label="类型">{selectedPosition.position_type}</Descriptions.Item>
              <Descriptions.Item label="经验要求">{selectedPosition.experience}</Descriptions.Item>
              <Descriptions.Item label="学历要求">{selectedPosition.education}</Descriptions.Item>
              <Descriptions.Item label="行业">{selectedPosition.industry}</Descriptions.Item>
              <Descriptions.Item label="发布日期">{selectedPosition.published_date || '未知'}</Descriptions.Item>
            </Descriptions>
            
            <Divider orientation="left">岗位要求</Divider>
            <div style={{ 
              background: '#f5f5f5', 
              padding: 16, 
              borderRadius: 8, 
              whiteSpace: 'pre-wrap',
              fontSize: 14,
              lineHeight: 1.6
            }}>
              {selectedPosition.requirements}
            </div>
            
            <Divider orientation="left">岗位描述</Divider>
            <div style={{ 
              background: '#f5f5f5', 
              padding: 16, 
              borderRadius: 8, 
              whiteSpace: 'pre-wrap',
              fontSize: 14,
              lineHeight: 1.6
            }}>
              {selectedPosition.description}
            </div>
            
            {selectedPosition.benefits && (
              <>
                <Divider orientation="left">福利待遇</Divider>
                <div style={{ 
                  background: '#f0f9ff', 
                  padding: 16, 
                  borderRadius: 8, 
                  whiteSpace: 'pre-wrap',
                  fontSize: 14,
                  lineHeight: 1.6
                }}>
                  {selectedPosition.benefits}
                </div>
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
