import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        timeout: 600000,  // 10 分钟（爬虫采集可能耗时较长）
        proxyTimeout: 600000,
      }
    }
  }
})
