import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, ShoppingCart, Sparkles, TrendingUp, RefreshCw } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useCart } from '@/contexts/CartContext';
import { useToast } from '@/hooks/use-toast';
import { getRecommendations, RecommendationScore } from '@/lib/recommendationEngine';
import { trackInteraction } from '@/lib/cartService';

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  
  const { user } = useAuth();
  const { addToCart, loading: cartLoading, items: cartItems } = useCart();
  const { toast } = useToast();

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const recs = await getRecommendations(8); // Get 8 recommendations
      setRecommendations(recs);
    } catch (err) {
      setError('Failed to load recommendations');
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      console.log('Fetching recommendations for user:', user.id, 'refreshKey:', refreshKey);
      fetchRecommendations();
    } else {
      // For non-logged users, show fallback recommendations
      console.log('No user logged in, showing fallback recommendations');
      const fetchFallback = async () => {
        try {
          setLoading(true);
          const { getFallbackRecommendations } = await import('@/lib/recommendationEngine');
          const fallbackRecs = getFallbackRecommendations(8);
          setRecommendations(fallbackRecs);
        } catch (err) {
          console.error('Error fetching fallback recommendations:', err);
          setError('Failed to load recommendations');
        } finally {
          setLoading(false);
        }
      };
      fetchFallback();
    }
  }, [user, refreshKey]); // Refetch when user changes or refresh is triggered

  // Refetch recommendations when cart items change (with debounce)
  useEffect(() => {
    if (!user) return;
    
    const timeoutId = setTimeout(() => {
      fetchRecommendations();
    }, 1000); // Debounce by 1 second to avoid too many requests

    return () => clearTimeout(timeoutId);
  }, [cartItems, user]);

  const handleProductClick = async (productId: number) => {
    if (user) {
      await trackInteraction(productId, 'view');
      // Trigger recommendations refresh after a short delay
      setTimeout(() => {
        setRefreshKey(prev => prev + 1);
      }, 500);
    }
  };

  const handleAddToCart = async (recommendation: RecommendationScore, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!user) {
      toast({
        title: "Please log in",
        description: "You need to be logged in to add items to cart.",
        variant: "destructive",
      });
      return;
    }

    try {
      // Convert recommendation product to cart-compatible format
      const cartProduct = {
        product_id: recommendation.product.product_id,
        product_name: recommendation.product.product_name,
        price: recommendation.product.price,
        image_url: recommendation.product.image_url,
      };
      
      await addToCart(cartProduct);
      toast({
        title: "Added to cart",
        description: `${recommendation.product.product_name} has been added to your cart.`,
      });
      
      // Trigger recommendations refresh after cart addition
      setTimeout(() => {
        setRefreshKey(prev => prev + 1);
      }, 1000);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add item to cart. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            Recommended for You
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4 overflow-x-auto">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex-shrink-0 w-64 h-80 bg-gray-200 rounded-lg animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mb-8">
        <CardContent className="p-6">
          <div className="text-center text-gray-500">
            <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (recommendations.length === 0) {
    return null; // Don't show anything if no recommendations
  }

  return (
    <Card className="mb-8">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-600" />
              {user ? 'Recommended for You' : 'Popular Products'}
            </CardTitle>
            {user && (
              <p className="text-sm text-gray-600 mt-1">
                Based on your browsing and shopping preferences
              </p>
            )}
          </div>
          {user && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setRefreshKey(prev => prev + 1)}
              disabled={loading}
              className="flex items-center gap-1"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex space-x-4 overflow-x-auto pb-4">
          {recommendations.map((recommendation) => (
            <div
              key={recommendation.product.product_id}
              className="flex-shrink-0 w-64 cursor-pointer"
              onClick={() => handleProductClick(recommendation.product.product_id)}
            >
              <Card className="h-full hover:shadow-lg transition-shadow duration-200">
                <div className="relative">
                  <img
                    src={recommendation.product.image_url}
                    alt={recommendation.product.product_name}
                    className="w-full h-40 object-cover rounded-t-lg"
                  />
                  {recommendation.product.is_on_sale && (
                    <Badge className="absolute top-2 left-2 bg-red-500 text-white">
                      Sale
                    </Badge>
                  )}
                  {recommendation.product.is_featured && (
                    <Badge className="absolute top-2 right-2 bg-blue-500 text-white">
                      Featured
                    </Badge>
                  )}
                </div>
                
                <CardContent className="p-4">
                  <h3 className="font-semibold text-sm mb-2 line-clamp-2">
                    {recommendation.product.product_name}
                  </h3>
                  
                  <div className="flex items-center mb-2">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="ml-1 text-sm font-medium">
                      {recommendation.product.rating}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      Score: {recommendation.score.toFixed(1)}
                    </span>
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mb-3">
                    {recommendation.reasons.slice(0, 2).map((reason, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {reason}
                      </Badge>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-gray-900">
                      ${recommendation.product.price}
                    </span>
                    
                    <Button
                      size="sm"
                      onClick={(e) => handleAddToCart(recommendation, e)}
                      disabled={cartLoading}
                      className="flex items-center space-x-1"
                    >
                      <ShoppingCart className="w-3 h-3" />
                      <span>{cartLoading ? 'Adding...' : 'Add'}</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default Recommendations; 