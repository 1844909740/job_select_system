import { Routes, Route, Navigate } from 'react-router-dom'
import { Result, Button } from 'antd'
import MainLayout from './components/Layout/MainLayout'
import Home from './pages/Home'
import Login from './pages/Login'
import Position from './pages/Position'
import Statistics from './pages/Statistics'
import AIAnalysis from './pages/AIAnalysis'
import Logs from './pages/Logs'
import Users from './pages/Users'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import useAuthStore from './store/authStore'

function PrivateRoute({ children }) {
  const token = useAuthStore((s) => s.token)
  return token ? children : <Navigate to="/login" replace />
}

function AdminRoute({ children }) {
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)
  if (!token) return <Navigate to="/login" replace />
  if (!user?.is_superuser && !user?.is_staff) {
    return (
      <Result
        status="403"
        title="无权访问"
        subTitle="此功能仅限管理员使用"
        extra={<Button type="primary" href="/">返回首页</Button>}
      />
    )
  }
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Home />} />
        <Route path="position" element={<PrivateRoute><Position /></PrivateRoute>} />
        <Route path="statistics" element={<PrivateRoute><Statistics /></PrivateRoute>} />
        <Route path="ai" element={<PrivateRoute><AIAnalysis /></PrivateRoute>} />
        <Route path="logs" element={<AdminRoute><Logs /></AdminRoute>} />
        <Route path="users" element={<AdminRoute><Users /></AdminRoute>} />
        <Route path="profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
      </Route>
    </Routes>
  )
}
