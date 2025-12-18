function getCatalogServiceUrl() {
  return import.meta.env.VITE_CATALOG_SERVICE_URL || '/api/catalog'
}

function resolveBaseUrl(base) {
  const s = String(base || '').trim()
  if (!s) return new URL('/api/catalog', window.location.origin)

  if (/^https?:\/\//i.test(s)) return new URL(s)

  return new URL(s, window.location.origin)
}

async function requestJson(pathname) {
  const base = resolveBaseUrl(getCatalogServiceUrl())
  const baseWithSlash = base.toString().endsWith('/') ? base.toString() : `${base.toString()}/`
  const url = new URL(pathname, baseWithSlash)

  const res = await fetch(url, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    // ignore
  }

  if (!res.ok) {
    const msg = data?.error ? String(data.error) : `HTTP ${res.status}`
    throw new Error(msg)
  }

  return data
}

function toUiProduct(p) {
  return {
    id: String(p.id),
    title: p.name,
    category: p.category,
    price: Number(p.price),
    currency: p.currency,
    desc: p.description,
    shipping_time: p.shipping_time,
    amount_available: p.amount_available,
    img: p.public_image_url,
  }
}

export async function listProducts() {
  const data = await requestJson('products')
  return Array.isArray(data?.products) ? data.products.map(toUiProduct) : []
}

export async function getProduct(id) {
  const data = await requestJson(`products/${encodeURIComponent(String(id))}`)
  return data?.product ? toUiProduct(data.product) : null
}
