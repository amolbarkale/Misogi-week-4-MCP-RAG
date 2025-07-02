import { supabase } from './supabaseClient';

export interface CartItem {
  user_id: string;
  product_id: number;
  quantity: number;
  added_at: string;
}

export interface Interaction {
  id: string;
  user_id: string;
  product_id: number;
  type: 'view' | 'add_to_cart' | 'remove_from_cart';
  created_at: string;
}

// Cart operations
export const addToCart = async (productId: number, quantity: number = 1): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    throw new Error('User must be logged in to add items to cart');
  }

  // Insert or update cart item
  const { error: cartError } = await supabase
    .from('cart_items')
    .upsert({
      user_id: user.id,
      product_id: productId,
      quantity
    }, {
      onConflict: 'user_id,product_id'
    });

  if (cartError) {
    throw new Error(`Failed to add to cart: ${cartError.message}`);
  }

  // Track interaction
  await trackInteraction(productId, 'add_to_cart');
};

export const removeFromCart = async (productId: number): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    throw new Error('User must be logged in');
  }

  // Remove from cart
  const { error: cartError } = await supabase
    .from('cart_items')
    .delete()
    .match({ user_id: user.id, product_id: productId });

  if (cartError) {
    throw new Error(`Failed to remove from cart: ${cartError.message}`);
  }

  // Track interaction
  await trackInteraction(productId, 'remove_from_cart');
};

export const updateCartQuantity = async (productId: number, quantity: number): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    throw new Error('User must be logged in');
  }

  if (quantity <= 0) {
    await removeFromCart(productId);
    return;
  }

  const { error } = await supabase
    .from('cart_items')
    .update({ quantity })
    .match({ user_id: user.id, product_id: productId });

  if (error) {
    throw new Error(`Failed to update quantity: ${error.message}`);
  }
};

export const getCartItems = async (): Promise<CartItem[]> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return [];
  }

  const { data, error } = await supabase
    .from('cart_items')
    .select('*')
    .eq('user_id', user.id)
    .order('added_at', { ascending: false });

  if (error) {
    throw new Error(`Failed to fetch cart items: ${error.message}`);
  }

  return data || [];
};

// Interaction tracking
export const trackInteraction = async (
  productId: number, 
  type: 'view' | 'add_to_cart' | 'remove_from_cart'
): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    // Don't track interactions for anonymous users
    return;
  }

  const { error } = await supabase
    .from('interactions')
    .insert({
      user_id: user.id,
      product_id: productId,
      type
    });

  if (error) {
    // Log error but don't throw - interaction tracking shouldn't block user actions
    console.warn('Failed to track interaction:', error.message);
  }
};

export const getUserInteractions = async (limit: number = 50): Promise<Interaction[]> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return [];
  }

  const { data, error } = await supabase
    .from('interactions')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .limit(limit);

  if (error) {
    throw new Error(`Failed to fetch interactions: ${error.message}`);
  }

  return data || [];
}; 