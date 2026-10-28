import express from 'express'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const production = process.argv.includes('--production') || process.env.NODE_ENV === 'production'
const root = fileURLToPath(new URL('.', import.meta.url))
const app = express()
app.disable('x-powered-by')
let vite

if (production) {
  app.use(express.static(`${root}dist/client`, { index: false }))
} else {
  const { createServer } = await import('vite')
  vite = await createServer({ root, server: { middlewareMode: true }, appType: 'custom' })
  app.use(vite.middlewares)
}

app.get('/', async (req, res) => {
  try {
    let template = await readFile(`${root}${production ? 'dist/client/' : ''}index.html`, 'utf8')
    if (vite) template = await vite.transformIndexHtml(req.originalUrl, template)
    const { render } = production
      ? await import('./dist/server/entry-server.js')
      : await vite.ssrLoadModule('/src/entry-server.js')
    const html = await render()
    res.type('html').send(template.replace('<!--ssr-outlet-->', () => html))
  } catch (error) {
    vite?.ssrFixStacktrace(error)
    console.error(error)
    res.status(500).type('text').send('Unable to load the shop. Please try again.')
  }
})

app.use((_req, res) => res.status(404).type('text').send('Page not found'))
const port = Number(process.env.PORT || 5173)
app.listen(port, '127.0.0.1', () => console.log(`Shop running at http://127.0.0.1:${port}`))
