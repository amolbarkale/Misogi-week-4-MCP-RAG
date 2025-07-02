import mockProducts from '../../mock_data.json';
import { getUserInteractions } from './cartService';

export interface Product {
  product_id: number;
  product_name: string;
  category: string;
  subcategory: string;
  price: number;
  rating: number;
  description: string;
  image_url: string;
  is_featured: boolean;
  is_on_sale: boolean;
}

export interface UserProfile {
  favoriteCategories: Record<string, number>;
  favoriteSubcategories: Record<string, number>;
  averagePriceRange: { min: number; max: number };
  interactionCount: number;
}

export interface RecommendationScore {
  product: Product;
  score: number;
  reasons: string[];
}

// Build user profile from interaction history
export const buildUserProfile = async (): Promise<UserProfile> => {
  const interactions = await getUserInteractions(50); // Get last 50 interactions
  
  const categoryCount: Record<string, number> = {};
  const subcategoryCount: Record<string, number> = {};
  const prices: number[] = [];
  
  // Analyze interaction patterns
  interactions.forEach(interaction => {
    const product = mockProducts.find(p => p.product_id === interaction.product_id);
    if (!product) return;
    
    // Weight different interaction types
    const weight = getInteractionWeight(interaction.type);
    
    // Count categories with weights
    categoryCount[product.category] = (categoryCount[product.category] || 0) + weight;
    subcategoryCount[product.subcategory] = (subcategoryCount[product.subcategory] || 0) + weight;
    
    // Collect prices for range analysis
    if (interaction.type === 'add_to_cart') {
      prices.push(product.price);
    }
  });
  
  // Calculate price range (if user has cart interactions)
  const averagePriceRange = prices.length > 0 
    ? {
        min: Math.min(...prices) * 0.7, // 30% below minimum
        max: Math.max(...prices) * 1.3   // 30% above maximum
      }
    : { min: 0, max: Infinity };
  
  return {
    favoriteCategories: categoryCount,
    favoriteSubcategories: subcategoryCount,
    averagePriceRange,
    interactionCount: interactions.length
  };
};

// Weight different interaction types
const getInteractionWeight = (type: string): number => {
  switch (type) {
    case 'add_to_cart': return 3;    // Strongest signal
    case 'view': return 1;           // Weakest signal
    case 'remove_from_cart': return -1; // Negative signal
    default: return 0;
  }
};

// Score a single product based on user profile
export const scoreProduct = (product: Product, userProfile: UserProfile): RecommendationScore => {
  let score = 0;
  const reasons: string[] = [];
  
  // Base score from product rating (0-1 scale)
  const ratingScore = product.rating / 5;
  score += ratingScore * 0.3; // 30% weight for rating
  if (product.rating >= 4.0) {
    reasons.push('Highly rated product');
  }
  
  // Category preference score (0-2 scale)
  const categoryPreference = userProfile.favoriteCategories[product.category] || 0;
  const maxCategoryPreference = Math.max(...Object.values(userProfile.favoriteCategories), 1);
  const categoryScore = (categoryPreference / maxCategoryPreference) * 2;
  score += categoryScore * 0.4; // 40% weight for category match
  if (categoryScore > 1) {
    reasons.push(`Matches your interest in ${product.category}`);
  }
  
  // Subcategory preference score (0-1 scale)
  const subcategoryPreference = userProfile.favoriteSubcategories[product.subcategory] || 0;
  const maxSubcategoryPreference = Math.max(...Object.values(userProfile.favoriteSubcategories), 1);
  const subcategoryScore = subcategoryPreference / maxSubcategoryPreference;
  score += subcategoryScore * 0.2; // 20% weight for subcategory match
  if (subcategoryScore > 0.5) {
    reasons.push(`Similar to ${product.subcategory} items you've liked`);
  }
  
  // Price range preference (0-1 scale)
  const { min, max } = userProfile.averagePriceRange;
  const priceScore = (product.price >= min && product.price <= max) ? 1 : 0.3;
  score += priceScore * 0.1; // 10% weight for price match
  if (priceScore === 1 && userProfile.interactionCount > 0) {
    reasons.push('Within your preferred price range');
  }
  
  // Bonus features
  if (product.is_featured) {
    score += 0.1;
    reasons.push('Featured product');
  }
  
  if (product.is_on_sale) {
    score += 0.15;
    reasons.push('Currently on sale');
  }
  
  return {
    product,
    score: Math.min(score, 5), // Cap at 5
    reasons
  };
};

// Get personalized recommendations
export const getRecommendations = async (limit: number = 10): Promise<RecommendationScore[]> => {
  const userProfile = await buildUserProfile();
  
  console.log('User profile:', {
    interactionCount: userProfile.interactionCount,
    favoriteCategories: userProfile.favoriteCategories,
    favoriteSubcategories: userProfile.favoriteSubcategories,
    priceRange: userProfile.averagePriceRange
  });
  
  // If user has no interactions, return popular/featured products
  if (userProfile.interactionCount === 0) {
    console.log('No interactions found, returning fallback recommendations');
    return getFallbackRecommendations(limit);
  }
  
  // Get products user hasn't interacted with
  const interactions = await getUserInteractions();
  const interactedProductIds = new Set(interactions.map(i => i.product_id));
  
  console.log('Interacted product IDs:', Array.from(interactedProductIds));
  
  const candidateProducts = mockProducts.filter(
    product => !interactedProductIds.has(product.product_id)
  );
  
  console.log(`Found ${candidateProducts.length} candidate products out of ${mockProducts.length} total products`);
  
  // Score all candidate products
  const scoredProducts = candidateProducts
    .map(product => scoreProduct(product as Product, userProfile))
    .sort((a, b) => b.score - a.score) // Sort by score descending
    .slice(0, limit);
  
  console.log('Top recommendations:', scoredProducts.slice(0, 3).map(r => ({
    name: r.product.product_name,
    category: r.product.category,
    score: r.score,
    reasons: r.reasons
  })));
  
  return scoredProducts;
};

// Fallback recommendations for new users
export const getFallbackRecommendations = (limit: number = 10): RecommendationScore[] => {
  const popularProducts = mockProducts
    .filter(product => product.is_featured || product.rating >= 4.0)
    .sort((a, b) => b.rating - a.rating)
    .slice(0, limit);
  
  return popularProducts.map(product => ({
    product: product as Product,
    score: product.rating,
    reasons: ['Popular choice', product.is_featured ? 'Featured product' : 'Highly rated']
  }));
};

// Get recommendations by category (for diversity)
export const getRecommendationsByCategory = async (category: string, limit: number = 5): Promise<RecommendationScore[]> => {
  const userProfile = await buildUserProfile();
  
  const categoryProducts = mockProducts
    .filter(product => product.category === category)
    .slice(0, limit * 2); // Get more candidates
  
  const scoredProducts = categoryProducts
    .map(product => scoreProduct(product as Product, userProfile))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
  
  return scoredProducts;
}; 