// 用户类型
export interface User {
  id: number;
  username: string;
  email?: string;
  avatar?: string;
  gender?: string;
  style_preference?: string;
  bio?: string;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  gender?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// 天气类型
export interface Weather {
  city: string;
  temperature: number;
  feels_like: number;
  humidity: number;
  wind_speed: number;
  weather: string;
  weather_code: number;
  description: string;
  aqi: number;
  uv_index: number;
  precipitation_probability: number;
}

export interface WeatherForecast {
  date: string;
  temperature_max: number;
  temperature_min: number;
  weather: string;
  weather_code: number;
  precipitation_probability: number;
  humidity: number;
  wind_speed: number;
}

export interface HourlyWeather {
  hour: string;
  temperature: number;
  weather: string;
  weather_code: number;
  precipitation_probability: number;
}

export interface AQIInfo {
  aqi: number;
  level: string;
  description: string;
  main_pollutant: string;
  advice: string;
}

export interface DressingAdvice {
  city: string;
  temperature: number;
  weather: string;
  advice: Array<{
    type: string;
    level: string;
    suggestion: string;
  }>;
}

// 衣服类型
export interface Clothes {
  id: number;
  user_id: number;
  image_url: string;
  name?: string;
  type: string;
  color?: string;
  material?: string;
  thickness?: string;
  style?: string;
  season?: string;
  formality?: number;  // 正式程度 1-5
  gender?: string;    // 适用性别
  temperature_min?: number;  // 适合最低温度
  temperature_max?: number;  // 适合最高温度
  tags?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface ClothesAnalysis {
  type: string;
  color: string;
  material: string;
  thickness: string;
  style: string;
  season?: string;
  formality?: number;
  gender?: string;
  temperature_min?: number;
  temperature_max?: number;
  confidence: number;
  notes?: string;
}

export interface ClothesListResponse {
  items: Clothes[];
  total: number;
  page: number;
  page_size: number;
}

export interface ClothesUploadResponse {
  image_url: string;
  analysis: ClothesAnalysis;
}

// 穿搭推荐类型
export interface OutfitItem {
  id: number;
  name: string;
  type: string;
  color: string;
  image_url: string;
}

export interface OutfitRecommendation {
  id?: string;  // UUID 字符串，用于收藏识别
  top?: OutfitItem;
  pants?: OutfitItem;
  shoes?: OutfitItem;
  jacket?: OutfitItem;
  accessories: OutfitItem[];
  reason: string;
  score: number;
  scene: string;
  tips: string[];
  date?: string;
  weather?: Weather;
}

export interface RecommendationRequest {
  city?: string;
  temperature?: number;
  weather?: string;
  scene?: string;
  style_preference?: string;
}

export interface SceneOption {
  value: string;
  label: string;
  icon: string;
}

export interface StyleOption {
  value: string;
  label: string;
  description: string;
}

// 聊天类型
export interface ChatMessage {
  id: number;
  message: string;
  response?: string;
  message_type: string;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  message_id: number;
  suggestions: string[];
}

// API 响应类型
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// 分页类型
export interface Pagination {
  page: number;
  page_size: number;
  total: number;
}

// 组件 Props 类型
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}
