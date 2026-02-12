import { useState, useEffect } from 'react'
import {
  Card, Row, Col, Button, Select, Input, Upload, Tabs, Tag, Table,
  Space, message, Spin, Descriptions, Empty, Divider, List,
} from 'antd'
import {
  RobotOutlined, UploadOutlined, ExperimentOutlined,
  ThunderboltOutlined, FileTextOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { aiAPI } from '../../api'

const ALGORITHMS = [
  { value: 'recommendation', label: '推荐岗位', color: '#00bebd', desc: '基于协同过滤，为你推荐最匹配的岗位' },
  { value: 'prediction', label: '趋势预测', color: '#1890ff', desc: '预测岗位未来需求与薪资趋势' },
  { value: 'classification', label: '职位分类', color: '#722ed1', desc: '按行业对相关岗位进行智能分类' },
  { value: 'clustering', label: '聚类分析', color: '#52c41a', desc: '将岗位按特征聚类为不同群组' },
  { value: 'nlp', label: '自然语言处理', color: '#eb2f96', desc: '从岗位要求中提取关键技能词汇' },
]

export default function AIAnalysis() {
  const [algorithm, setAlgorithm] = useState('recommendation')
  const [resumeText, setResumeText] = useState('')
  const [fileList, setFileList] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [tasks, setTasks] = useState([])

  useEffect(() => { loadTasks() }, [])

  const loadTasks = async () => {
    try {
      const { data } = await aiAPI.tasks.list()
      setTasks((data.results || data || []).slice(0, 10))
    } catch {}
  }

  // ====== 简历分析 ======
  const handleResumeAnalysis = async () => {
    if (!resumeText.trim() && fileList.length === 0) return message.warning('请粘贴简历内容或上传简历文件')
    setLoading(true)
    setResult(null)
    try {
      let payload
      if (fileList.length > 0 && fileList[0].originFileObj) {
        payload = new FormData()
        payload.append('resume_file', fileList[0].originFileObj)
        payload.append('algorithm_type', algorithm)
      } else {
        payload = { resume_text: resumeText.trim(), algorithm_type: algorithm }
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
                    <Card size="small" style={{ borderTop: `3px solid ${['#00bebd', '#1890ff', '#fa8c16'][i]}` }}>
                      <Descriptions column={1} size="small">
                        <Descriptions.Item label="群组">{c.name}</Descriptions.Item>
                        <Descriptions.Item label="数量">{c.size} 个</Descriptions.Item>
                        <Descriptions.Item label="平均薪资">{c.avg_salary}K</Descriptions.Item>
                        {c.features && <Descriptions.Item label="特征">{c.features}</Descriptions.Item>}
                      </Descriptions>
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

      {/* 简历分析区域 */}
      <div className="table-card">
        <div className="category-tabs" style={{ marginBottom: 0 }}>
          <div className="category-tab active">
            <FileTextOutlined style={{ marginRight: 4 }} />上传简历分析
          </div>
        </div>

        <div style={{ padding: '24px 0' }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} md={16}>
              <Input.TextArea
                rows={8}
                placeholder="粘贴你的简历内容...&#10;&#10;例如：&#10;姓名：张三&#10;技能：Python, Django, React, MySQL, Redis&#10;经验：3年后端开发经验&#10;学历：本科 计算机科学&#10;项目经历：负责过电商系统开发..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
              />
            </Col>
            <Col xs={24} md={8}>
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
    </div>
  )
}
