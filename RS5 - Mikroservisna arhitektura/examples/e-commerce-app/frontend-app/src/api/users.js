function getUserServiceUrl() {
  // In dev, default goes through Vite proxy.
  // For prod builds, set VITE_USER_SERVICE_URL to your user-service origin.
  return import.meta.env.VITE_USER_SERVICE_URL || '/api/users'
}

function resolveBaseUrl(base) {
  const s = String(base || '').trim()
  if (!s) return new URL('/api/users', window.location.origin)

  // Absolute URL?
  if (/^https?:\/\//i.test(s)) return new URL(s)

  // Path-only base -> make it absolute to current origin.
  return new URL(s, window.location.origin)
}

async function requestJson(pathname, { method = 'GET', body } = {}) {
  const base = resolveBaseUrl(getUserServiceUrl())
  const baseWithSlash = base.toString().endsWith('/') ? base.toString() : `${base.toString()}/`
  const url = new URL(pathname, baseWithSlash)

  const hasBody = body !== undefined

  const res = await fetch(url, {
    method,
    headers: {
      Accept: 'application/json',
      ...(hasBody ? { 'Content-Type': 'application/json' } : {}),
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

export async function listUsers() {
  const data = await requestJson('users')
  return Array.isArray(data?.users) ? data.users : []
}

export async function ensureUser({ email, connection }) {
  const data = await requestJson('users', {
    method: 'POST',
    body: { email, connection },
  })
  return data
}

export async function getUserByEmail(email) {
  const users = await listUsers()
  const needle = String(email || '')
    .trim()
    .toLowerCase()
  return (
    users.find(
      (u) =>
        String(u?.email || '')
          .trim()
          .toLowerCase() === needle,
    ) || null
  )
}

export function inferConnectionFromAuthUser(authUser) {
  const sub = authUser?.sub ? String(authUser.sub) : ''
  if (sub.includes('|')) return sub.split('|')[0]
  return sub || 'auth0'
}

