import type { User as SupabaseUser } from '@supabase/supabase-js'

export interface User {
  id: string;
  email: string;
  name?: string; // optional since Supabase doesn't require display name
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  signUp: (email: string, password: string, name?: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

export interface SignUpData {
  email: string;
  password: string;
  confirmPassword: string;
  name: string;
}

export interface SignInData {
  email: string;
  password: string;
}

// Helper to convert Supabase user to our User type
export const mapSupabaseUser = (supabaseUser: SupabaseUser): User => ({
  id: supabaseUser.id,
  email: supabaseUser.email!,
  name: supabaseUser.user_metadata?.name || supabaseUser.email?.split('@')[0],
  created_at: supabaseUser.created_at
})
