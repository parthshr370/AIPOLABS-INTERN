import { supabase, persistSession, getElementById } from './authShared'

async function initializeLoginForm(): Promise<void> {
  const form = getElementById<HTMLFormElement>('login')
  const emailInput = getElementById<HTMLInputElement>('email')
  const passwordInput = getElementById<HTMLInputElement>('password')
  const statusDiv = getElementById<HTMLDivElement>('status')

  if (!form || !emailInput || !passwordInput) {
    console.error('Login form not found')
    return
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    
    // Show loading state
    if (statusDiv) {
      statusDiv.textContent = 'Signing in...'
      statusDiv.className = 'status'
      statusDiv.style.display = 'block'
    }

    const email = emailInput.value.trim()
    const password = passwordInput.value

    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })

      if (error) {
        console.error('Sign-in error:', error)
        if (statusDiv) {
          statusDiv.textContent = `Error: ${error.message}`
          statusDiv.className = 'status error'
          statusDiv.style.display = 'block'
        }
        return
      }

      await persistSession(data.session)
      
      if (statusDiv) {
        statusDiv.textContent = 'Signed in successfully! Redirecting...'
        statusDiv.className = 'status success'
        statusDiv.style.display = 'block'
      }

      setTimeout(() => {
        window.location.href = 'quick-guide.html'
      }, 1500)

    } catch (error) {
      console.error('Login failed:', error)
      if (statusDiv) {
        statusDiv.textContent = 'Login failed. Please try again.'
        statusDiv.className = 'status error'
        statusDiv.style.display = 'block'
      }
    }
  })
}

initializeLoginForm()


