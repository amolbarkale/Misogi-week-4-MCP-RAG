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

## Phase 2 – Frontend auth integration ✅

- [x] ~~**Add env vars** `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` → `.env.local`~~
- [x] ~~**Add `src/lib/supabaseClient.ts`** that calls `createClient(...)`~~
- [x] ~~**Replace local `AuthContext` with Supabase session context**~~
  - ~~Signup / Login modals call `supabase.auth.signUp` / `signInWithPassword`~~
  - ~~Store user session; subscribe to `supabase.auth.onAuthStateChange`~~
- [x] ~~**Fix modal closing after successful login/signup**~~

## Phase 3 – Cart & Interaction tracking

- [x] ~~**Implement `addToCart` & `removeFromCart` helpers** (update `cart_items`, insert into `interactions`)~~
- [x] ~~**Track product `view` interactions** when a `ProductCard` is clicked~~

## Phase 4 – Recommendation engine ✅ COMPLETED

- [x] ~~**Content-based recommendation algorithm** (rule-based scorer with category preferences, rating, price range)~~
- [x] ~~**User profile builder** from interaction history~~
- [x] ~~**Product scoring system** with weighted factors (40% category match, 30% rating, 20% subcategory, 10% price)~~
- [x] ~~**Create `<Recommendations />` component** that fetches and renders personalized suggestions~~
- [x] ~~**Integration with main catalog** replacing placeholder section~~


- [ ] **Update README** with setup + run instructions 