// /src/api/mockData.ts
import { Customer } from '../components/CustomerTable';

const firstNames = ['张', '李', '王', '刘', '陈', '杨', '黄', '赵', '周', '吴'];
const lastNames = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '洋', '艳'];
const sources = ['淘宝', '微信', '线下推广', '转介绍', '其他'];
const regions = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '南京', '重庆'];
const grades = ['小学', '初中', '高中', '大学'];
const statuses: Array<'active' | 'inactive' | 'pending'> = ['active', 'inactive', 'pending'];

// 生成200条模拟客户数据
export const generateMockCustomers = (count: number = 200): Customer[] => {
  return Array.from({ length: count }, (_, index) => {
    const id = index + 1;
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    
    return {
      id,
      name: `${firstName}${lastName}`,
      phone: `138${String(10000000 + Math.floor(Math.random() * 90000000)).padStart(8, '0')}`,
      email: Math.random() > 0.3 ? `user${id}@example.com` : undefined,
      status,
      source: sources[Math.floor(Math.random() * sources.length)],
      revenue: Math.floor(Math.random() * 50000) + 1000,
      createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
      region: regions[Math.floor(Math.random() * regions.length)],
      grade: Math.random() > 0.3 ? grades[Math.floor(Math.random() * grades.length)] : undefined,
      gender: Math.random() > 0.5 ? '男' : '女'
    };
  });
};

// KPI 统计数据
export interface KpiStats {
  totalCustomers: number;
  activeCustomers: number;
  totalRevenue: number;
  averageRevenue: number;
  conversionRate: number;
  monthlyGrowth: number;
}

export const calculateKpiStats = (customers: Customer[]): KpiStats => {
  const total = customers.length;
  const active = customers.filter(c => c.status === 'active').length;
  const totalRevenue = customers.reduce((sum, c) => sum + c.revenue, 0);
  const averageRevenue = total > 0 ? totalRevenue / total : 0;
  const conversionRate = total > 0 ? (active / total) * 100 : 0;
  const monthlyGrowth = 12.5; // 模拟月增长率

  return {
    totalCustomers: total,
    activeCustomers: active,
    totalRevenue,
    averageRevenue,
    conversionRate,
    monthlyGrowth
  };
};

// 模拟 API 调用
export const api = {
  // 获取客户列表
  getCustomers: async (params?: {
    page?: number;
    pageSize?: number;
    search?: string;
    status?: string;
  }): Promise<{ data: Customer[]; total: number }> => {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    
    let customers = generateMockCustomers(200);
    
    // 搜索过滤
    if (params?.search) {
      const search = params.search.toLowerCase();
      customers = customers.filter(c => 
        c.name.includes(search) || 
        c.phone.includes(search) ||
        c.email?.includes(search)
      );
    }
    
    // 状态过滤
    if (params?.status) {
      customers = customers.filter(c => c.status === params.status);
    }
    
    // 分页
    const page = params?.page || 1;
    const pageSize = params?.pageSize || 50;
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    
    return {
      data: customers.slice(start, end),
      total: customers.length
    };
  },

  // 获取单个客户详情
  getCustomer: async (id: number): Promise<Customer | null> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const customers = generateMockCustomers(200);
    return customers.find(c => c.id === id) || null;
  },

  // 创建客户
  createCustomer: async (data: Partial<Customer>): Promise<Customer> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return {
      id: Date.now(),
      name: data.name || '',
      phone: data.phone || '',
      email: data.email,
      status: data.status || 'pending',
      source: data.source || '其他',
      revenue: data.revenue || 0,
      createdAt: new Date().toISOString(),
      region: data.region,
      grade: data.grade,
      gender: data.gender
    };
  },

  // 更新客户
  updateCustomer: async (id: number, data: Partial<Customer>): Promise<Customer> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const customer = await api.getCustomer(id);
    if (!customer) throw new Error('客户不存在');
    
    return {
      ...customer,
      ...data,
      id // 确保ID不被覆盖
    };
  },

  // 删除客户
  deleteCustomer: async (id: number): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    // 模拟删除操作
  },

  // 获取 KPI 统计
  getKpiStats: async (): Promise<KpiStats> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const customers = generateMockCustomers(200);
    return calculateKpiStats(customers);
  },

  // 获取趋势数据
  getTrendData: async (range: 'week' | 'month' | 'year'): Promise<Array<{ date: string; value: number }>> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const days = range === 'week' ? 7 : range === 'month' ? 30 : 365;
    const data = [];
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      data.push({
        date: date.toISOString().split('T')[0],
        value: Math.floor(Math.random() * 50000) + 30000
      });
    }
    
    return data;
  },

  // 获取渠道分布数据
  getChannelData: async (): Promise<Array<{ channel: string; value: number; percentage: number }>> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const channels = [
      { channel: '淘宝', value: 450000 },
      { channel: '微信', value: 320000 },
      { channel: '线下推广', value: 180000 },
      { channel: '转介绍', value: 150000 },
      { channel: '其他', value: 80000 }
    ];
    
    const total = channels.reduce((sum, c) => sum + c.value, 0);
    
    return channels.map(c => ({
      ...c,
      percentage: Number(((c.value / total) * 100).toFixed(1))
    }));
  }
};