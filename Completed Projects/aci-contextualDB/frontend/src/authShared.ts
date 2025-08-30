import { createClient, type Session } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://qbrrnndopducbuqwvsfg.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFicnJubmRvcGR1Y2J1cXd2c2ZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MTY3MDcsImV4cCI6MjA3MTA5MjcwN30.0oXgGT2upAYtkvdc4N_B7oxZSgwbs35b_7litO020Zk'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    autoRefreshToken: true,
    persistSession: false,
    detectSessionInUrl: false,
  },
})

export async function persistSession(session: Session | null): Promise<void> {
  if (!session) {
    await chrome.storage.local.remove(['access_token', 'refresh_token', 'user'])
    return
  }

  const { access_token, refresh_token, user } = session
  await chrome.storage.local.set({ access_token, refresh_token, user })
}

// Keep storage in sync if the token refreshes in the background
supabase.auth.onAuthStateChange(async (_event: string, session: Session | null) => {
  await persistSession(session)
})

export function getElementById<T extends HTMLElement>(id: string): T | null {
  return document.getElementById(id) as T | null
}


