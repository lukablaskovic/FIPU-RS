import assert from 'node:assert/strict'
import { test } from 'node:test'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import { render } from '../dist/server/entry-server.js'
import { products, formatPrice } from '../src/data/products.js'

test('renders the catalog with a fresh cart for each request', async () => {
  const first = await render()
  for (const product of products) assert.ok(first.includes(product.name))
  assert.equal(products.length, 30)
  assert.equal(new Set(products.map((product) => product.id)).size, 30)
  assert.equal(new Set(products.map((product) => product.category)).size, 3)
  assert.equal((first.match(/<img /g) || []).length, 31)
  assert.equal((first.match(/<article/g) || []).length, 30)
  for (let index = 0; index < 3; index++) {
    assert.ok(first.includes(`href="#category-${index}"`))
    assert.ok(first.includes(`id="category-${index}"`))
  }
  assert.ok(!first.includes('The everyday collection'))
  assert.ok(!first.includes('id="cart"'))
  assert.ok(!first.includes('href="#cart"'))
  assert.ok(!first.includes('Demo shop'))
  assert.equal(await render(), first)
  assert.equal(formatPrice(1250), '€12.50')
})

test('production serves rendered HTML, built assets, and real 404s', async () => {
  const server = spawn(process.execPath, ['server.js', '--production'], {
    env: { ...process.env, PORT: '15173' }, stdio: ['ignore', 'pipe', 'pipe'],
  })
  try {
    await Promise.race([
      once(server.stdout, 'data'),
      once(server, 'exit').then(() => { throw new Error('Server exited before startup') }),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Startup timed out')), 10000).unref()),
    ])
    const response = await fetch('http://127.0.0.1:15173/')
    assert.equal(response.status, 200)
    const html = await response.text()
    assert.ok(html.includes(products[0].name))
    assert.ok(!html.includes('<!--ssr-outlet-->'))
    const assets = [...html.matchAll(/(?:src|href)="(\/assets\/[^\"]+)"/g)]
    assert.ok(assets.length >= 2)
    for (const [, path] of assets) {
      assert.equal((await fetch(`http://127.0.0.1:15173${path}`)).status, 200)
    }
    for (const product of products) {
      const image = await fetch(`http://127.0.0.1:15173${product.image}`)
      assert.equal(image.status, 200)
      assert.ok(image.headers.get('content-type').startsWith('image/'))
      assert.ok((await image.arrayBuffer()).byteLength > 100)
    }
    assert.equal((await fetch('http://127.0.0.1:15173/missing')).status, 404)
  } finally {
    const exited = once(server, 'exit')
    server.kill()
    await exited
  }
})


test('cart is hidden when empty and renders selected items and their total', async () => {
  const { createServer } = await import('vite')
  const vite = await createServer({ server: { middlewareMode: true, hmr: { port: 15174 } }, appType: 'custom' })
  try {
    const { default: ShoppingCart } = await vite.ssrLoadModule('/src/components/ShoppingCart.vue')
    const { createSSRApp } = await import('vue')
    const { renderToString } = await import('vue/server-renderer')
    const empty = await renderToString(createSSRApp(ShoppingCart, { items: [] }))
    assert.ok(!empty.includes('id="cart"'))
    const items = [products[0], products[1], products[0]]
    const html = await renderToString(createSSRApp(ShoppingCart, { items }))
    assert.ok(html.includes('id="cart"'))
    assert.ok(html.includes(`${products[0].name} × 2 · ${formatPrice(products[0].price * 2)}`))
    assert.ok(html.includes(`${products[1].name} × 1`))
    assert.ok(html.includes('3 items'))
    assert.equal(items.length, 3)
    const remaining = items.filter((product) => product.id !== products[0].id)
    const afterRemoval = await renderToString(createSSRApp(ShoppingCart, { items: remaining }))
    assert.ok(!afterRemoval.includes(products[0].name))
    assert.ok(afterRemoval.includes(products[1].name))
    assert.ok(html.includes('fixed inset-x-0 bottom-0'))
    assert.equal((html.match(/<li /g) || []).length, 2)
    assert.ok(html.includes(formatPrice(items.reduce((sum, item) => sum + item.price, 0))))
    assert.ok(html.includes(`Remove all ${products[0].name} from cart`))
    assert.ok(!html.includes('Demo shop'))
    for (const product of [products[0], products[1]]) {
      assert.ok(html.includes(`Increase quantity of ${product.name}`))
      assert.ok(html.includes(`Decrease quantity of ${product.name}`))
    }
    items.push(products[0])
    const increased = await renderToString(createSSRApp(ShoppingCart, { items }))
    assert.ok(increased.includes(`${products[0].name} × 3 · ${formatPrice(products[0].price * 3)}`))
    items.splice(items.indexOf(products[0]), 1)
    const decreased = await renderToString(createSSRApp(ShoppingCart, { items }))
    assert.ok(decreased.includes(`${products[0].name} × 2`))
    items.splice(items.indexOf(products[1]), 1)
    const removedLast = await renderToString(createSSRApp(ShoppingCart, { items }))
    assert.ok(!removedLast.includes(products[1].name))
  } finally {
    await vite.close()
  }
})
