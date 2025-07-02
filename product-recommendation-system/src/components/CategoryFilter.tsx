
import React from 'react';
import { Badge } from '@/components/ui/badge';

interface CategoryFilterProps {
  categories: string[];
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
}

const CategoryFilter: React.FC<CategoryFilterProps> = ({
  categories,
  selectedCategory,
  onCategoryChange,
}) => {
  return (
    <div className="flex flex-wrap gap-2 mb-8">
      <Badge 
        variant={selectedCategory === 'All' ? 'default' : 'outline'}
        className="cursor-pointer px-4 py-2 text-sm hover:bg-blue-100 transition-colors duration-200"
        onClick={() => onCategoryChange('All')}
      >
        All Products
      </Badge>
      {categories.map((category) => (
        <Badge
          key={category}
          variant={selectedCategory === category ? 'default' : 'outline'}
          className="cursor-pointer px-4 py-2 text-sm hover:bg-blue-100 transition-colors duration-200"
          onClick={() => onCategoryChange(category)}
        >
          {category}
        </Badge>
      ))}
    </div>
  );
};

export default CategoryFilter;
