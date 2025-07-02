# MVP Roadmap – Supabase × React Product-Recommendation App

> Mark each task with ~~strikethrough~~ once you've finished it. We'll keep updating this file as we progress.

## Phase 1 – Supabase back-end

- [x] ~~**Create Supabase project** in the Supabase dashboard~~
- [x] ~~**Enable Email/Password authentication** (`Auth → Settings → Email`)~~
- [x] ~~**Grab project credentials**~~
  - ~~Project URL~~
  - ~~`anon` public key~~
- [x] ~~**Create `interaction_type` enum**~~
- [x] ~~**Create `interactions` table** `(id, user_id, product_id, type, created_at)`~~
- [x] ~~**Create RLS policies for `interactions`** (user can insert & read own rows)~~
- [x] ~~**Create `cart_items` table** `(user_id, product_id, quantity, added_at)`~~
- [x] ~~**Create RLS policies for `cart_items`** (CRUD limited to owner)~~
- [ ] (Optional) **Create `profiles` table** `(id, username, avatar_url)` + RLS

## Phase 2 – Frontend auth integration

- [ ] **Add env vars** `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` → `.env.local`
- [x] ~~**Add `src/lib/supabaseClient.ts`** that calls `createClient(...)`~~
- [ ] **Replace local `AuthContext` with Supabase session context**
  - Signup / Login modals call `supabase.auth.signUp` / `signInWithPassword`
  - Store user session; subscribe to `supabase.auth.onAuthStateChange`

## Phase 3 – Cart & Interaction tracking

- [ ] **Implement `addToCart` & `removeFromCart` helpers** (update `cart_items`, insert into `interactions`)
- [ ] **Track product `view` interactions** when a `ProductCard` is clicked

## Phase 4 – Recommendation engine

- [ ] **Edge Function `get_recommendations`** (rule-based scorer)
- [ ] **Expose REST endpoint** `/recommendations`
- [ ] **Create `<Recommendations />` component** that fetches and renders the list above the catalog

## Phase 5 – Testing & Polish

- [ ] **Unit tests** for scoring & helper functions (Vitest)
- [ ] **Integration tests** mocking Supabase to ensure interactions & cart flow work
- [ ] **Update README** with setup + run instructions 