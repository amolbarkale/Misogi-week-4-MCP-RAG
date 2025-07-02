import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useAuth } from './AuthContext';
import * as cartService from '@/lib/cartService';
import mockProducts from '../../mock_data.json';

interface CartItem {
  id: number;
  name: string;
  price: number;
  image: string;
  quantity: number;
}

interface CartContextType {
  items: CartItem[];
  addToCart: (product: any) => Promise<void>;
  removeFromCart: (id: number) => Promise<void>;
  updateQuantity: (id: number, quantity: number) => Promise<void>;
  getTotalItems: () => number;
  getTotalPrice: () => number;
  isCartOpen: boolean;
  setIsCartOpen: (open: boolean) => void;
  loading: boolean;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [items, setItems] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  // Load cart items when user changes
  useEffect(() => {
    const loadCartItems = async () => {
      if (!user) {
        setItems([]);
        return;
      }

      setLoading(true);
      try {
        const cartItems = await cartService.getCartItems();
        
        // Convert Supabase cart items to UI cart items by matching with mock products
        const uiCartItems: CartItem[] = cartItems
          .map(cartItem => {
            const product = mockProducts.find(p => p.product_id === cartItem.product_id);
            if (!product) return null;
            
            return {
              id: product.product_id,
              name: product.product_name,
              price: product.price,
              image: product.image_url,
              quantity: cartItem.quantity
            };
          })
          .filter(Boolean) as CartItem[];

        setItems(uiCartItems);
      } catch (error) {
        console.error('Failed to load cart items:', error);
      } finally {
        setLoading(false);
      }
    };

    loadCartItems();
  }, [user]);

  const addToCart = async (product: any) => {
    if (!user) {
      throw new Error('Please log in to add items to cart');
    }

    setLoading(true);
    try {
      // Use product_id if available, otherwise use id
      const productId = product.product_id || product.id;
      await cartService.addToCart(productId, 1);
      
      // Update local state
      setItems(prev => {
        const existingItem = prev.find(item => item.id === productId);
        if (existingItem) {
          return prev.map(item =>
            item.id === productId
              ? { ...item, quantity: item.quantity + 1 }
              : item
          );
        }
        return [...prev, { 
          id: productId,
          name: product.product_name || product.name,
          price: product.price,
          image: product.image_url || product.image,
          quantity: 1 
        }];
      });
    } catch (error) {
      console.error('Failed to add to cart:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (id: number) => {
    if (!user) {
      throw new Error('Please log in to modify cart');
    }

    setLoading(true);
    try {
      await cartService.removeFromCart(id);
      
      // Update local state
      setItems(prev => prev.filter(item => item.id !== id));
    } catch (error) {
      console.error('Failed to remove from cart:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (id: number, quantity: number) => {
    if (!user) {
      throw new Error('Please log in to modify cart');
    }

    if (quantity <= 0) {
      await removeFromCart(id);
      return;
    }

    setLoading(true);
    try {
      await cartService.updateCartQuantity(id, quantity);
      
      // Update local state
      setItems(prev =>
        prev.map(item =>
          item.id === id ? { ...item, quantity } : item
        )
      );
    } catch (error) {
      console.error('Failed to update quantity:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getTotalItems = () => {
    return items.reduce((total, item) => total + item.quantity, 0);
  };

  const getTotalPrice = () => {
    return items.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  return (
    <CartContext.Provider value={{
      items,
      addToCart,
      removeFromCart,
      updateQuantity,
      getTotalItems,
      getTotalPrice,
      isCartOpen,
      setIsCartOpen,
      loading
    }}>
      {children}
    </CartContext.Provider>
  );
};
