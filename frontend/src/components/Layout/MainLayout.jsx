import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { Dropdown, Avatar, message } from 'antd'
import { UserOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons'
import useAuthStore from '../../store/authStore'

export default function MainLayout() {
  const { user, token, logout } = useAuthStore()
  const navigate = useNavigate()
  const isAdmin = user?.is_superuser || user?.is_staff

  const handleLogout = () => {
    logout()
    message.success('已退出登录')
    navigate('/')
  }

  const userMenuItems = [
    { key: 'profile', icon: <UserOutlined />, label: '个人资料' },
    { key: 'settings', icon: <SettingOutlined />, label: '系统设置' },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
  ]

  const onMenuClick = ({ key }) => {
    if (key === 'logout') handleLogout()
    else if (key === 'profile') navigate('/profile')
    else if (key === 'settings') navigate('/settings')
  }

  return (
    <div className="site-layout">
      {/* 顶部导航 */}
      <header className="site-header">
        <div className="header-inner">
          <div className="header-logo" onClick={() => navigate('/')}>
            职位分析系统
          </div>

          <nav className="header-nav">
            <NavLink to="/" end>首页</NavLink>
            <NavLink to="/position">职位</NavLink>
            {isAdmin && <NavLink to="/data">数据采集</NavLink>}
            <NavLink to="/statistics">统计分析</NavLink>
            <NavLink to="/ai">AI分析</NavLink>
            {isAdmin && <NavLink to="/logs">操作日志</NavLink>}
            {isAdmin && <NavLink to="/users">用户管理</NavLink>}
          </nav>

          <div className="header-right">
            {token ? (
              <Dropdown menu={{ items: userMenuItems, onClick: onMenuClick }} placement="bottomRight">
                <div className="header-user">
                  <Avatar size={32} icon={<UserOutlined />} style={{ backgroundColor: 'rgba(255,255,255,0.3)' }} />
                  <span>{user?.username || '用户'}</span>
                </div>
              </Dropdown>
            ) : (
              <div style={{ display: 'flex', gap: 12 }}>
                <span style={{ cursor: 'pointer', fontSize: 14 }} onClick={() => navigate('/login')}>登录</span>
                <span style={{ cursor: 'pointer', fontSize: 14 }} onClick={() => navigate('/login?tab=register')}>注册</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 页面内容 */}
      <Outlet />

      {/* 页脚 */}
      <footer className="site-footer">
        <div className="footer-inner">
          <div className="footer-col">
            <h4>职位分析系统</h4>
            <a href="#">关于我们</a>
            <a href="#">使用帮助</a>
            <a href="#">协议与规则</a>
          </div>
          <div className="footer-col">
            <h4>核心功能</h4>
            <a href="#">岗位数据查询</a>
            <a href="#">统计分析</a>
            <a href="#">AI智能分析</a>
          </div>
          <div className="footer-col">
            <h4>数据服务</h4>
            <a href="#">数据采集管理</a>
            <a href="#">可视化展示</a>
            <a href="#">操作日志</a>
          </div>
          <div className="footer-col">
            <h4>联系我们</h4>
            <a href="#">技术支持</a>
            <a href="#">意见反馈</a>
          </div>
        </div>
        <div className="footer-bottom">
          Copyright &copy; 2026 职位分析系统 · 毕业设计项目
        </div>
      </footer>
    </div>
  )
}
