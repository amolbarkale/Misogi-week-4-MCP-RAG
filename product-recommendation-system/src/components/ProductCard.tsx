
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, ShoppingCart } from 'lucide-react';

interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  originalPrice?: number;
  description: string;
  rating: number;
  reviews: number;
  image: string;
  tags: string[];
}

interface ProductCardProps {
  product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  const discountPercentage = product.originalPrice 
    ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
    : 0;

  return (
    <Card className="group cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1 bg-white border border-gray-200">
      <div className="relative overflow-hidden rounded-t-lg">
        <img 
          src={product.image} 
          alt={product.name}
          className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {discountPercentage > 0 && (
          <Badge className="absolute top-2 left-2 bg-red-500 hover:bg-red-600 text-white">
            -{discountPercentage}%
          </Badge>
        )}
      </div>
      
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-lg text-gray-900 group-hover:text-blue-600 transition-colors duration-200 line-clamp-2">
            {product.name}
          </h3>
        </div>
        
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {product.description}
        </p>
        
        <div className="flex items-center mb-3">
          <div className="flex items-center">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="ml-1 text-sm font-medium text-gray-700">
              {product.rating}
            </span>
          </div>
          <span className="ml-2 text-xs text-gray-500">
            ({product.reviews} reviews)
          </span>
        </div>
        
        <div className="flex flex-wrap gap-1 mb-3">
          {product.tags.slice(0, 2).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold text-gray-900">
              ${product.price}
            </span>
            {product.originalPrice && (
              <span className="text-sm text-gray-500 line-through">
                ${product.originalPrice}
              </span>
            )}
          </div>
          
          <button className="flex items-center space-x-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg transition-colors duration-200 text-sm font-medium">
            <ShoppingCart className="w-4 h-4" />
            <span>Add</span>
          </button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProductCard;
