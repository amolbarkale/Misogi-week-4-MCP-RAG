import { createClient } from '@supabase/supabase-js'

// Make sure you have copied `env.example` to `.env.local` and filled in the real keys.
// Vite exposes env vars prefixed with `VITE_` to the browser at build/runtime.

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string

if (!supabaseUrl || !supabaseAnonKey) {
  // eslint-disable-next-line no-console
  console.warn('Supabase credentials are not set. Add them to .env.local')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey) 