import { supabase, persistSession, getElementById } from './authShared'

async function initializeSignupForm(): Promise<void> {
  const form = getElementById<HTMLFormElement>('signup')
  const emailInput = getElementById<HTMLInputElement>('email')
  const passwordInput = getElementById<HTMLInputElement>('password')
  const statusDiv = getElementById<HTMLDivElement>('status')

  if (!form || !emailInput || !passwordInput) {
    console.error('Signup form not found')
    return
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    
    // Show loading state
    if (statusDiv) {
      statusDiv.textContent = 'Creating account...'
      statusDiv.className = 'status'
      statusDiv.style.display = 'block'
    }

    const email = emailInput.value.trim()
    const password = passwordInput.value

    try {
      const { data, error } = await supabase.auth.signUp({ email, password })

      if (error) {
        console.error('Sign-up error:', error)
        if (statusDiv) {
          statusDiv.textContent = `Error: ${error.message}`
          statusDiv.className = 'status error'
          statusDiv.style.display = 'block'
        }
        return
      }

      // If email confirmation is enabled, session may be null until confirmation
      await persistSession(data.session ?? null)
      
      if (data.session) {
        // User is signed in immediately (no email confirmation required)
        if (statusDiv) {
          statusDiv.textContent = 'Account created successfully! Redirecting...'
          statusDiv.className = 'status success'
          statusDiv.style.display = 'block'
        }
        
        // Redirect to usage instructions
        setTimeout(() => {
          window.location.href = 'quick-guide.html'
        }, 1500)
      } else {
        // Email confirmation required
        if (statusDiv) {
          statusDiv.textContent = 'Account created! Check your email to confirm your account.'
          statusDiv.className = 'status success'
          statusDiv.style.display = 'block'
        }
      }

    } catch (error) {
      console.error('Signup failed:', error)
      if (statusDiv) {
        statusDiv.textContent = 'Signup failed. Please try again.'
        statusDiv.className = 'status error'
        statusDiv.style.display = 'block'
      }
    }
  })
}

initializeSignupForm()


