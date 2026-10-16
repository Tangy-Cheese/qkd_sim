import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import process from 'node:process'

// https://vite.dev/config/
export default defineConfig({
  // GitHub Pages serves the site from /<repo>/, so the deploy workflow sets VITE_BASE. Locally it stays at /
  base: process.env.VITE_BASE ?? '/',
  plugins: [react()],
  server: {
    // The frontend calls /api/..., which is forwarded to the FastAPI backend (uvicorn on port 8000)
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
