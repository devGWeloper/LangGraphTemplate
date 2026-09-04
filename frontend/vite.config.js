import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 개발 중에는 npm run dev (5173) 로 띄우고, /api 요청은 백엔드(8021)로 넘깁니다.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8021' },
  },
})
