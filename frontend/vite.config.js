import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import process from 'node:process'
import mdx from '@mdx-js/rollup'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'

// https://vite.dev/config/
export default defineConfig({
  // GitHub Pages serves the site from /<repo>/, so the deploy workflow sets VITE_BASE. Locally it stays at /
  base: process.env.VITE_BASE ?? '/',
  plugins: [
    // .mdx pages: Markdown with LaTeX maths, rendered to HTML by KaTeX at build time
    { enforce: 'pre', ...mdx({ remarkPlugins: [remarkGfm, remarkMath], rehypePlugins: [rehypeKatex] }) },
    react({ include: /\.(jsx|js|mdx)$/ }),
  ],
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
