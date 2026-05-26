import { type ClassValue, clsx } from 'clsx';

// 合并 className
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// 格式化日期
export function formatDate(date: string | Date, format: string = 'YYYY-MM-DD'): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hour = String(d.getHours()).padStart(2, '0');
  const minute = String(d.getMinutes()).padStart(2, '0');
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute);
}

// 获取星期几
export function getWeekday(date: string | Date): string {
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  const d = typeof date === 'string' ? new Date(date) : date;
  return weekdays[d.getDay()];
}

// 天气代码转中文
export function weatherCodeToText(code: number): string {
  const weatherMap: Record<number, string> = {
    100: '晴',
    101: '多云',
    102: '少云',
    103: '晴间多云',
    104: '阴',
    200: '有风',
    201: '平静',
    202: '微风',
    203: '和风',
    204: '清风',
    205: '强风',
    206: '大风',
    207: '烈风',
    208: '风暴',
    209: '狂风暴雨',
    210: '雷阵雨',
    211: '雷阵雨',
    212: '雷阵雨',
    300: '小雨',
    301: '中雨',
    302: '大雨',
    303: '极端降雨',
    304: '冻雨',
    305: '小阵雨',
    306: '中阵雨',
    307: '大阵雨',
    308: '强阵雨',
    309: '小毛毛雨',
    310: '中毛毛雨',
    311: '大毛毛雨',
    312: '大毛毛雨',
    313: '阵雨夹雪',
    400: '小雪',
    401: '中雪',
    402: '大雪',
    403: '暴雪',
    404: '雨夹雪',
    405: '雪雨',
    406: '阵雨夹雪',
    407: '阵雪',
    500: '薄雾',
    501: '雾',
    502: '浓雾',
    503: '大雾',
    504: '冻结雾',
    507: '远方闪电',
    508: '雷暴',
    509: '大雷暴',
    510: '小雷暴',
    511: '雷暴',
    512: '强雷暴',
    513: '雷暴夹冰雹',
    514: '雷暴夹冰雹',
    515: '雷暴夹冰雹',
  };
  
  return weatherMap[code] || '未知';
}

// 天气代码转图标
export function weatherCodeToIcon(code: number): string {
  if (code === 100) return '☀️'; // 晴
  if (code <= 104) return '⛅'; // 多云
  if (code >= 200 && code <= 299) return '💨'; // 风
  if (code >= 300 && code <= 399) return '🌧️'; // 雨
  if (code >= 400 && code <= 499) return '❄️'; // 雪
  if (code >= 500 && code <= 599) return '🌫️'; // 雾
  if (code >= 600 && code <= 699) return '🌨️'; // 冻
  if (code >= 700 && code <= 799) return '🌫️'; // 其他
  if (code >= 800) return '🌤️'; // 极端天气
  return '🌤️';
}

// 温度颜色
export function temperatureColor(temp: number): string {
  if (temp <= 0) return 'text-blue-600';
  if (temp <= 10) return 'text-blue-400';
  if (temp <= 20) return 'text-green-500';
  if (temp <= 25) return 'text-yellow-500';
  if (temp <= 30) return 'text-orange-500';
  return 'text-red-500';
}

// AQI 颜色
export function aqiColor(aqi: number): string {
  if (aqi <= 50) return 'bg-green-500';
  if (aqi <= 100) return 'bg-yellow-500';
  if (aqi <= 150) return 'bg-orange-500';
  if (aqi <= 200) return 'bg-red-500';
  if (aqi <= 300) return 'bg-purple-500';
  return 'bg-maroon-500';
}

// AQI 等级
export function aqiLevel(aqi: number): string {
  if (aqi <= 50) return '优';
  if (aqi <= 100) return '良';
  if (aqi <= 150) return '轻度污染';
  if (aqi <= 200) return '中度污染';
  if (aqi <= 300) return '重度污染';
  return '严重污染';
}

// 风速等级
export function windLevel(speed: number): string {
  if (speed <= 1) return '静风';
  if (speed <= 5) return '软风';
  if (speed <= 11) return '轻风';
  if (speed <= 19) return '微风';
  if (speed <= 28) return '和风';
  if (speed <= 38) return '劲风';
  if (speed <= 49) return '强风';
  if (speed <= 61) return '疾风';
  return '大风';
}

// 衣服类型中文
export function clothesTypeToText(type: string): string {
  const typeMap: Record<string, string> = {
    top: '上衣',
    tshirt: 'T恤',
    shirt: '衬衫',
    sweater: '毛衣',
    hoodie: '卫衣',
    pants: '裤子',
    jeans: '牛仔裤',
    shorts: '短裤',
    skirt: '裙子',
    shoes: '鞋子',
    sneaker: '运动鞋',
    jacket: '外套',
    coat: '大衣',
    windbreaker: '风衣',
    accessory: '配饰',
  };
  return typeMap[type] || type;
}

// 场景中文
export function sceneToText(scene: string): string {
  const sceneMap: Record<string, string> = {
    daily: '日常',
    work: '上班',
    date: '约会',
    sports: '运动',
    party: '聚会',
    travel: '出行',
  };
  return sceneMap[scene] || scene;
}

// 生成随机ID
export function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

// 防抖函数
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

// 节流函数
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}
