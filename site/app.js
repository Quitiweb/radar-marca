import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'

const SUPABASE_URL = 'https://krvjpugpnmxevgvaqges.supabase.co'
const SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_m2ter4mlET-DZz9ztJvJwQ_29Kucdsy'

const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)

const authCard = document.getElementById('auth-card')
const dashboard = document.getElementById('dashboard')
const googleLoginBtn = document.getElementById('google-login')
const logoutBtn = document.getElementById('logout-btn')
const brandForm = document.getElementById('brand-form')
const brandsEmpty = document.getElementById('brands-empty')
const brandsList = document.getElementById('brands-list')
const userName = document.getElementById('user-name')
const userEmail = document.getElementById('user-email')
const appAlert = document.getElementById('app-alert')

let currentWorkspace = null

function showAlert(message, kind = 'info') {
  appAlert.hidden = false
  appAlert.textContent = message
  appAlert.className = `card notice notice-${kind}`
}

function clearAlert() {
  appAlert.hidden = true
  appAlert.textContent = ''
  appAlert.className = 'card notice'
}

function normalizeDomain(value) {
  return value.trim().toLowerCase().replace(/^https?:\/\//, '').replace(/\/$/, '')
}

async function signInWithGoogle() {
  const redirectTo = `${window.location.origin}${window.location.pathname}`
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo },
  })
  if (error) showAlert(error.message, 'error')
}

async function signOut() {
  await supabase.auth.signOut()
  window.location.reload()
}

async function ensureWorkspace(user) {
  const { data: workspaces, error } = await supabase
    .from('workspaces')
    .select('*')
    .eq('owner_user_id', user.id)
    .limit(1)

  if (error) throw error
  if (workspaces && workspaces.length) return workspaces[0]

  const fallbackName = user.user_metadata?.full_name || user.email?.split('@')[0] || 'Workspace'
  const { data: inserted, error: insertError } = await supabase
    .from('workspaces')
    .insert({ name: fallbackName, owner_user_id: user.id })
    .select()
    .single()

  if (insertError) throw insertError
  return inserted
}

function renderBrands(brands) {
  brandsList.innerHTML = ''
  if (!brands.length) {
    brandsEmpty.hidden = false
    brandsList.hidden = true
    return
  }

  brandsEmpty.hidden = true
  brandsList.hidden = false
  for (const brand of brands) {
    const article = document.createElement('article')
    article.className = 'card'
    article.innerHTML = `
      <span class="eyebrow">Marca</span>
      <h3>${brand.name}</h3>
      <p><strong>Dominio principal:</strong> ${brand.primary_domain}</p>
      <p><strong>Objetivo:</strong> ${brand.goal || '-'}</p>
      <p><strong>Sector:</strong> ${brand.industry || '-'}</p>
    `
    brandsList.appendChild(article)
  }
}

async function loadBrands() {
  if (!currentWorkspace) return
  const { data, error } = await supabase
    .from('brands')
    .select('*')
    .eq('workspace_id', currentWorkspace.id)
    .order('created_at', { ascending: false })

  if (error) throw error
  renderBrands(data || [])
}

async function createBrand(event) {
  event.preventDefault()
  clearAlert()
  if (!currentWorkspace) return

  const name = document.getElementById('brand-name').value.trim()
  const primaryDomain = normalizeDomain(document.getElementById('brand-domain').value)
  const industry = document.getElementById('brand-industry').value.trim()
  const goal = document.getElementById('brand-goal').value

  if (!name || !primaryDomain) {
    showAlert('Marca y dominio principal son obligatorios.', 'error')
    return
  }

  const { data: brand, error } = await supabase
    .from('brands')
    .insert({
      workspace_id: currentWorkspace.id,
      name,
      primary_domain: primaryDomain,
      industry: industry || null,
      goal,
    })
    .select()
    .single()

  if (error) {
    showAlert(error.message, 'error')
    return
  }

  const { error: domainError } = await supabase
    .from('brand_domains')
    .insert({
      brand_id: brand.id,
      domain: primaryDomain,
      kind: 'legitimate',
    })

  if (domainError) {
    showAlert(domainError.message, 'error')
    return
  }

  brandForm.reset()
  showAlert('Marca guardada correctamente.', 'success')
  await loadBrands()
}

async function hydrate(session) {
  if (!session?.user) {
    authCard.hidden = false
    dashboard.hidden = true
    return
  }

  authCard.hidden = true
  dashboard.hidden = false
  userName.textContent = session.user.user_metadata?.full_name || session.user.email || 'Usuario'
  userEmail.textContent = session.user.email || ''

  currentWorkspace = await ensureWorkspace(session.user)
  await loadBrands()
}

async function init() {
  clearAlert()
  googleLoginBtn?.addEventListener('click', signInWithGoogle)
  logoutBtn?.addEventListener('click', signOut)
  brandForm?.addEventListener('submit', createBrand)

  const { data, error } = await supabase.auth.getSession()
  if (error) {
    showAlert(error.message, 'error')
    return
  }
  await hydrate(data.session)

  supabase.auth.onAuthStateChange(async (_event, session) => {
    await hydrate(session)
  })
}

init().catch((error) => {
  console.error(error)
  showAlert(error.message || 'Ha ocurrido un error inesperado.', 'error')
})
