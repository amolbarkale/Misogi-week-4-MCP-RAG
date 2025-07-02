
import React, { useState } from 'react';
import { useCart } from '@/contexts/CartContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ShoppingCart, User, LogOut } from 'lucide-react';
import AuthModal from './auth/AuthModal';

const Header: React.FC = () => {
  const { getTotalItems, setIsCartOpen } = useCart();
  const { user, signOut, loading } = useAuth();
  const [authModalOpen, setAuthModalOpen] = useState(false);

  const handleAuthClick = () => {
    if (user) {
      signOut();
    } else {
      setAuthModalOpen(true);
    }
  };

  return (
    <>
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Product Store</h1>
          <div className="flex items-center space-x-4">
            {user && (
              <span className="text-sm text-gray-600 hidden sm:block">
                Welcome, {user.name}
              </span>
            )}
            <Button 
              variant="ghost" 
              size="icon"
              onClick={handleAuthClick}
              disabled={loading}
            >
              {user ? (
                <LogOut className="w-5 h-5" />
              ) : (
                <User className="w-5 h-5" />
              )}
              <span className="sr-only">
                {user ? 'Logout' : 'Login'}
              </span>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="relative"
              onClick={() => setIsCartOpen(true)}
            >
              <ShoppingCart className="w-5 h-5" />
              {getTotalItems() > 0 && (
                <Badge className="absolute -top-2 -right-2 w-5 h-5 rounded-full p-0 flex items-center justify-center text-xs">
                  {getTotalItems()}
                </Badge>
              )}
            </Button>
          </div>
        </div>
      </header>

      <AuthModal 
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
      />
    </>
  );
};

export default Header;
