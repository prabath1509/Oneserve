import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendTarget = 'http://localhost:8000'
const proxiedPaths = [
  '/auth',
  '/complaints',
  '/locker',
  '/certificates',
  '/notifications',
  '/dashboard',
  '/admin',
  '/files',
  '/health',
  '/docs',
  '/openapi.json',
  '/redoc'
]

const proxy = Object.fromEntries(
  proxiedPaths.map((path) => [
    path,
    {
      target: backendTarget,
      changeOrigin: true,
    },
  ])
)

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy
  }
})
