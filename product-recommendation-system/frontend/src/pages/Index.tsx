
import React from 'react';
import ProductCatalog from '@/components/ProductCatalog';
import { CartProvider } from '@/contexts/CartContext';
import { AuthProvider } from '@/contexts/AuthContext';

const Index = () => {
  return (
    <AuthProvider>
      <CartProvider>
        <ProductCatalog />
      </CartProvider>
    </AuthProvider>
  );
};

export default Index;
