function getOrderServiceUrl() {
  // In dev, default goes through Vite proxy.
  // For prod builds, set VITE_ORDER_SERVICE_URL to your order-service origin.
  return import.meta.env.VITE_ORDER_SERVICE_URL || '/api/orders'
}

function resolveBaseUrl(base) {
  const s = String(base || '').trim()
  if (!s) return new URL('/api/orders', window.location.origin)

  // Absolute URL?
  if (/^https?:\/\//i.test(s)) return new URL(s)

  // Path-only base (e.g. "/api/orders") -> make it absolute to current origin.
  return new URL(s, window.location.origin)
}

async function requestJson(pathname, { method = 'GET', body, accessToken } = {}) {
  const base = resolveBaseUrl(getOrderServiceUrl())
  const baseWithSlash = base.toString().endsWith('/') ? base.toString() : `${base.toString()}/`
  const url = new URL(pathname, baseWithSlash)

  const hasBody = body !== undefined

  const res = await fetch(url, {
    method,
    headers: {
      Accept: 'application/json',
      ...(hasBody ? { 'Content-Type': 'application/json' } : {}),
      ...(accessToken ? { Authorization: `Bearer ${String(accessToken)}` } : {}),
    },
    body: hasBody ? JSON.stringify(body) : undefined,
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

export async function createOrder(payload, { accessToken } = {}) {
  return await requestJson('orders', { method: 'POST', body: payload, accessToken })
}

export async function listOrders() {
  const data = await requestJson('orders')
  return Array.isArray(data?.orders) ? data.orders : []
}

export async function getOrder(id) {
  const data = await requestJson(`orders/${encodeURIComponent(String(id))}`)
  return data?.order ?? null
}

export async function listOrdersByUserId(userId, { accessToken } = {}) {
  const data = await requestJson(`orders/user/${encodeURIComponent(String(userId))}`, {
    accessToken,
  })
  return Array.isArray(data?.orders) ? data.orders : []
}
