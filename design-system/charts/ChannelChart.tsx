import React, { useRef, useEffect, useState, useMemo } from 'react';
import Chart from 'chart.js/auto';
import { ChartConfiguration } from 'chart.js';

// 数据点 Schema
export interface ChannelDataPoint {
  channel: string;
  value: number;
  percentage: number;
  metadata?: {
    customers?: number;
    averageValue?: number;
    conversionRate?: number;
    [key: string]: any;
  };
}

// 组件 Props
export interface ChannelChartProps {
  data: ChannelDataPoint[];
  type?: 'pie' | 'doughnut';
  onSegmentClick?: (segment: ChannelDataPoint) => void;
  height?: number;
  loading?: boolean;
  showLegend?: boolean;
  showPercentage?: boolean;
  exportFileName?: string;
  colorScheme?: 'default' | 'warm' | 'cool' | 'custom';
  customColors?: string[];
}

// JSON Schema
export const ChannelDataSchema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["channel", "value", "percentage"],
    "properties": {
      "channel": {
        "type": "string",
        "description": "渠道名称"
      },
      "value": {
        "type": "number",
        "description": "渠道数值（收入或客户数）"
      },
      "percentage": {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "description": "占比百分比"
      },
      "metadata": {
        "type": "object",
        "properties": {
          "customers": {
            "type": "integer",
            "description": "客户数量"
          },
          "averageValue": {
            "type": "number",
            "description": "平均价值"
          },
          "conversionRate": {
            "type": "number",
            "description": "转化率"
          }
        }
      }
    }
  }
};

// Mock Data Generator
export const generateMockChannelData = (): ChannelDataPoint[] => {
  const channels = [
    { name: '淘宝', baseValue: 450000, customers: 856 },
    { name: '微信', baseValue: 320000, customers: 623 },
    { name: '线下推广', baseValue: 180000, customers: 245 },
    { name: '转介绍', baseValue: 150000, customers: 198 },
    { name: '其他', baseValue: 80000, customers: 112 }
  ];
  
  const total = channels.reduce((sum, c) => sum + c.baseValue, 0);
  
  return channels.map(channel => ({
    channel: channel.name,
    value: channel.baseValue,
    percentage: Number((channel.baseValue / total * 100).toFixed(1)),
    metadata: {
      customers: channel.customers,
      averageValue: Math.round(channel.baseValue / channel.customers),
      conversionRate: Number((Math.random() * 30 + 50).toFixed(1))
    }
  }));
};

// 颜色方案
const colorSchemes = {
  default: [
    '#4A90E2', // 蓝色
    '#52C41A', // 绿色
    '#FF9500', // 橙色
    '#7C3AED', // 紫色
    '#17A2B8', // 青色
    '#DC3545', // 红色
    '#6C757D', // 灰色
  ],
  warm: [
    '#FF6B6B',
    '#FFA500',
    '#FFD700',
    '#FF8C00',
    '#FF6347',
    '#FF4500',
    '#DC143C'
  ],
  cool: [
    '#4ECDC4',
    '#45B7D1',
    '#6C5CE7',
    '#A8E6CF',
    '#81ECEC',
    '#74B9FF',
    '#A29BFE'
  ]
};

export const ChannelChart: React.FC<ChannelChartProps> = ({
  data,
  type = 'doughnut',
  onSegmentClick,
  height = 300,
  loading = false,
  showLegend = true,
  showPercentage = true,
  exportFileName = 'channel-distribution',
  colorScheme = 'default',
  customColors
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);
  const [hoveredSegment, setHoveredSegment] = useState<string | null>(null);

  // 计算总值
  const totalValue = useMemo(() => 
    data.reduce((sum, item) => sum + item.value, 0),
    [data]
  );

  // 获取颜色
  const getColors = useMemo(() => {
    if (customColors && customColors.length >= data.length) {
      return customColors;
    }
    return colorScheme === 'custom' ? colorSchemes.default : colorSchemes[colorScheme];
  }, [colorScheme, customColors, data.length]);

  // 导出为PNG
  const exportToPNG = () => {
    if (!canvasRef.current) return;
    
    const link = document.createElement('a');
    link.download = `${exportFileName}-${new Date().toISOString().split('T')[0]}.png`;
    link.href = canvasRef.current.toDataURL();
    link.click();
  };

  // 导出为CSV
  const exportToCSV = () => {
    const headers = ['渠道', '数值', '占比(%)', '客户数', '平均价值', '转化率(%)'];
    const rows = data.map(item => [
      item.channel,
      item.value,
      item.percentage,
      item.metadata?.customers || '',
      item.metadata?.averageValue || '',
      item.metadata?.conversionRate || ''
    ]);
    
    const csv = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${exportFileName}-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  // 获取表格化数据
  const getTableData = () => {
    return {
      headers: ['渠道', '收入', '占比', '客户数'],
      rows: data.map(item => [
        item.channel,
        `¥${item.value.toLocaleString()}`,
        `${item.percentage}%`,
        item.metadata?.customers?.toLocaleString() || '-'
      ])
    };
  };

  useEffect(() => {
    if (!canvasRef.current || loading) return;

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    // 准备图表数据
    const chartData = {
      labels: data.map(item => item.channel),
      datasets: [{
        data: data.map(item => item.value),
        backgroundColor: data.map((_, index) => 
          getColors[index % getColors.length]
        ),
        borderWidth: 2,
        borderColor: '#fff',
        hoverOffset: 4
      }]
    };

    const config: ChartConfiguration = {
      type: type,
      data: chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: type === 'doughnut' ? '50%' : undefined,
        plugins: {
          legend: {
            display: showLegend,
            position: 'right',
            labels: {
              padding: 15,
              usePointStyle: true,
              font: {
                size: 12
              },
              generateLabels: (chart) => {
                const dataset = chart.data.datasets[0];
                return chart.data.labels?.map((label, i) => ({
                  text: showPercentage 
                    ? `${label} (${data[i].percentage}%)`
                    : label as string,
                  fillStyle: dataset.backgroundColor?.[i] as string,
                  strokeStyle: dataset.borderColor as string,
                  lineWidth: dataset.borderWidth as number,
                  hidden: false,
                  index: i
                })) || [];
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            cornerRadius: 8,
            titleFont: {
              size: 14,
              weight: '600'
            },
            bodyFont: {
              size: 13
            },
            callbacks: {
              title: (items) => {
                if (!items.length) return '';
                return data[items[0].dataIndex].channel;
              },
              label: (context) => {
                const item = data[context.dataIndex];
                const lines = [
                  `收入: ¥${item.value.toLocaleString()}`,
                  `占比: ${item.percentage}%`
                ];
                
                if (item.metadata) {
                  if (item.metadata.customers) {
                    lines.push(`客户数: ${item.metadata.customers.toLocaleString()}`);
                  }
                  if (item.metadata.averageValue) {
                    lines.push(`客单价: ¥${item.metadata.averageValue.toLocaleString()}`);
                  }
                  if (item.metadata.conversionRate) {
                    lines.push(`转化率: ${item.metadata.conversionRate}%`);
                  }
                }
                
                return lines;
              }
            }
          },
          datalabels: showPercentage ? {
            color: '#fff',
            font: {
              weight: 'bold',
              size: 14
            },
            formatter: (value, context) => {
              return data[context.dataIndex].percentage + '%';
            }
          } : false
        },
        onClick: (event, elements) => {
          if (elements.length > 0 && onSegmentClick) {
            const index = elements[0].index;
            onSegmentClick(data[index]);
          }
        },
        onHover: (event, elements) => {
          if (canvasRef.current) {
            canvasRef.current.style.cursor = elements.length > 0 ? 'pointer' : 'default';
          }
          
          if (elements.length > 0) {
            const index = elements[0].index;
            setHoveredSegment(data[index].channel);
          } else {
            setHoveredSegment(null);
          }
        }
      }
    };

    // 销毁旧图表
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    // 创建新图表
    chartRef.current = new Chart(ctx, config);

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [data, type, showLegend, showPercentage, onSegmentClick, loading, getColors]);

  if (loading) {
    return (
      <div className="channel-chart-loading" style={{ height }}>
        <div className="spinner"></div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="channel-chart-container">
      <div className="channel-chart-toolbar">
        <button onClick={exportToPNG} className="export-btn" aria-label="导出为PNG">
          <i className="fas fa-image"></i> PNG
        </button>
        <button onClick={exportToCSV} className="export-btn" aria-label="导出为CSV">
          <i className="fas fa-file-csv"></i> CSV
        </button>
      </div>
      
      <div className="channel-chart-wrapper" style={{ height }}>
        <canvas 
          ref={canvasRef}
          role="img"
          aria-label="渠道分布图表"
        />
        
        {/* 中心统计信息（仅环形图） */}
        {type === 'doughnut' && (
          <div className="channel-chart-center">
            <div className="center-value">¥{totalValue.toLocaleString()}</div>
            <div className="center-label">总收入</div>
          </div>
        )}
      </div>
      
      {/* 悬停信息面板 */}
      {hoveredSegment && (
        <div className="channel-info-panel">
          <h4>{hoveredSegment}</h4>
          {data.find(d => d.channel === hoveredSegment)?.metadata && (
            <div className="info-details">
              <span>点击查看详情</span>
            </div>
          )}
        </div>
      )}
      
      {/* 屏幕阅读器友好的表格版本 */}
      <div className="sr-only">
        <table>
          <caption>渠道分布数据表</caption>
          <thead>
            <tr>
              {getTableData().headers.map((header, i) => (
                <th key={i}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {getTableData().rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td key={j}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// CSS Styles
export const channelChartStyles = `
.channel-chart-container {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
}

.channel-chart-toolbar {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
  z-index: 10;
}

.channel-chart-wrapper {
  position: relative;
}

.channel-chart-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.center-value {
  font-size: 24px;
  font-weight: 700;
  color: #212529;
}

.center-label {
  font-size: 14px;
  color: #6c757d;
  margin-top: 4px;
}

.channel-info-panel {
  position: absolute;
  bottom: 16px;
  left: 16px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  pointer-events: none;
  opacity: 0;
  animation: fadeIn 0.2s forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.channel-info-panel h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.info-details {
  font-size: 12px;
  opacity: 0.8;
}

.export-btn {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.export-btn:hover {
  background: #f5f5f5;
  border-color: #4A90E2;
}

.channel-chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4A90E2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .channel-chart-container {
    padding: 12px;
  }
  
  .channel-chart-toolbar {
    position: static;
    margin-bottom: 12px;
    justify-content: flex-end;
  }
  
  .center-value {
    font-size: 20px;
  }
  
  .center-label {
    font-size: 12px;
  }
}
`;