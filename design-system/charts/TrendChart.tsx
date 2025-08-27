import React, { useRef, useEffect, useState, useMemo } from 'react';
import Chart from 'chart.js/auto';
import { ChartConfiguration, TooltipItem } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { zhCN } from 'date-fns/locale';

// 数据点 Schema
export interface TrendDataPoint {
  timestamp: string; // ISO 8601 格式
  value: number;
  series: string;
  metadata?: {
    count?: number;
    average?: number;
    [key: string]: any;
  };
}

// 组件 Props
export interface TrendChartProps {
  data: TrendDataPoint[];
  timeRange: 'day' | 'week' | 'month' | 'quarter' | 'year';
  onPointClick?: (point: TrendDataPoint) => void;
  onRangeChange?: (range: { start: Date; end: Date }) => void;
  height?: number;
  loading?: boolean;
  showLegend?: boolean;
  enableZoom?: boolean;
  maxPoints?: number; // 性能优化：最大显示点数
  exportFileName?: string;
}

// JSON Schema
export const TrendDataSchema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["timestamp", "value", "series"],
    "properties": {
      "timestamp": {
        "type": "string",
        "format": "date-time",
        "description": "ISO 8601 格式的时间戳"
      },
      "value": {
        "type": "number",
        "description": "数据值"
      },
      "series": {
        "type": "string",
        "description": "数据系列名称"
      },
      "metadata": {
        "type": "object",
        "description": "附加元数据"
      }
    }
  }
};

// Mock Data Generator
export const generateMockTrendData = (days: number = 30): TrendDataPoint[] => {
  const data: TrendDataPoint[] = [];
  const series = ['试听课收入', '正课收入', '续课收入'];
  const now = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    series.forEach(seriesName => {
      const baseValue = seriesName === '正课收入' ? 50000 : 
                       seriesName === '试听课收入' ? 10000 : 30000;
      const randomFactor = 0.8 + Math.random() * 0.4;
      const trend = i / days * 0.3; // 增长趋势
      
      data.push({
        timestamp: date.toISOString(),
        value: Math.round(baseValue * randomFactor * (1 + trend)),
        series: seriesName,
        metadata: {
          count: Math.floor(10 + Math.random() * 50),
          average: Math.round(baseValue / (10 + Math.random() * 10))
        }
      });
    });
  }
  
  return data;
};

export const TrendChart: React.FC<TrendChartProps> = ({
  data,
  timeRange,
  onPointClick,
  onRangeChange,
  height = 300,
  loading = false,
  showLegend = true,
  enableZoom = true,
  maxPoints = 1000,
  exportFileName = 'trend-chart'
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);
  const [selectedRange, setSelectedRange] = useState<{ start: Date; end: Date } | null>(null);

  // 数据降采样
  const downsampledData = useMemo(() => {
    if (data.length <= maxPoints) return data;
    
    const factor = Math.ceil(data.length / maxPoints);
    return data.filter((_, index) => index % factor === 0);
  }, [data, maxPoints]);

  // 数据聚合
  const aggregateData = useMemo(() => {
    const grouped = new Map<string, Map<string, TrendDataPoint[]>>();
    
    downsampledData.forEach(point => {
      const date = new Date(point.timestamp);
      let key: string;
      
      switch (timeRange) {
        case 'day':
          key = date.toISOString().split('T')[0];
          break;
        case 'week':
          const weekStart = new Date(date);
          weekStart.setDate(date.getDate() - date.getDay());
          key = weekStart.toISOString().split('T')[0];
          break;
        case 'month':
          key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
          break;
        case 'quarter':
          const quarter = Math.floor(date.getMonth() / 3) + 1;
          key = `${date.getFullYear()}-Q${quarter}`;
          break;
        case 'year':
          key = String(date.getFullYear());
          break;
      }
      
      if (!grouped.has(point.series)) {
        grouped.set(point.series, new Map());
      }
      
      const seriesMap = grouped.get(point.series)!;
      if (!seriesMap.has(key)) {
        seriesMap.set(key, []);
      }
      
      seriesMap.get(key)!.push(point);
    });
    
    // 计算聚合值
    const result: TrendDataPoint[] = [];
    grouped.forEach((seriesMap, seriesName) => {
      seriesMap.forEach((points, dateKey) => {
        const sum = points.reduce((acc, p) => acc + p.value, 0);
        const avg = sum / points.length;
        
        result.push({
          timestamp: points[0].timestamp,
          value: Math.round(avg),
          series: seriesName,
          metadata: {
            count: points.length,
            sum: sum,
            average: avg,
            min: Math.min(...points.map(p => p.value)),
            max: Math.max(...points.map(p => p.value))
          }
        });
      });
    });
    
    return result.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  }, [downsampledData, timeRange]);

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
    const headers = ['时间戳', '系列', '数值', '数量', '平均值'];
    const rows = aggregateData.map(point => [
      point.timestamp,
      point.series,
      point.value,
      point.metadata?.count || '',
      point.metadata?.average || ''
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

  // 获取表格化数据（用于屏幕阅读器）
  const getTableData = () => {
    const series = Array.from(new Set(aggregateData.map(d => d.series)));
    const dates = Array.from(new Set(aggregateData.map(d => d.timestamp)));
    
    return {
      headers: ['日期', ...series],
      rows: dates.map(date => {
        const row = [new Date(date).toLocaleDateString('zh-CN')];
        series.forEach(s => {
          const point = aggregateData.find(d => d.timestamp === date && d.series === s);
          row.push(point ? point.value.toLocaleString() : '0');
        });
        return row;
      })
    };
  };

  useEffect(() => {
    if (!canvasRef.current || loading) return;

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    // 准备图表数据
    const datasets = Array.from(
      new Set(aggregateData.map(d => d.series))
    ).map((series, index) => {
      const seriesData = aggregateData
        .filter(d => d.series === series)
        .map(d => ({
          x: new Date(d.timestamp),
          y: d.value,
          metadata: d.metadata
        }));

      const colors = [
        'rgb(74, 144, 226)',
        'rgb(82, 196, 26)', 
        'rgb(255, 149, 0)',
        'rgb(124, 58, 237)'
      ];

      return {
        label: series,
        data: seriesData,
        borderColor: colors[index % colors.length],
        backgroundColor: colors[index % colors.length] + '20',
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.2,
        fill: false
      };
    });

    const config: ChartConfiguration = {
      type: 'line',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          title: {
            display: false
          },
          legend: {
            display: showLegend,
            position: 'bottom',
            labels: {
              padding: 15,
              usePointStyle: true,
              font: {
                size: 12
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
                const date = new Date(items[0].parsed.x);
                return date.toLocaleDateString('zh-CN', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                });
              },
              label: (context) => {
                const point = aggregateData.find(
                  d => d.series === context.dataset.label && 
                       new Date(d.timestamp).getTime() === context.parsed.x
                );
                
                const lines = [
                  `${context.dataset.label}: ¥${context.parsed.y.toLocaleString()}`
                ];
                
                if (point?.metadata) {
                  if (point.metadata.count) {
                    lines.push(`数量: ${point.metadata.count}`);
                  }
                  if (point.metadata.average) {
                    lines.push(`平均: ¥${Math.round(point.metadata.average).toLocaleString()}`);
                  }
                }
                
                return lines;
              }
            }
          },
          zoom: enableZoom ? {
            zoom: {
              wheel: {
                enabled: true,
              },
              pinch: {
                enabled: true
              },
              mode: 'x',
              onZoomComplete: ({chart}) => {
                const {min, max} = chart.scales.x;
                if (onRangeChange) {
                  onRangeChange({
                    start: new Date(min),
                    end: new Date(max)
                  });
                }
              }
            },
            pan: {
              enabled: true,
              mode: 'x'
            }
          } : undefined
        },
        scales: {
          x: {
            type: 'time',
            adapters: {
              date: {
                locale: zhCN
              }
            },
            time: {
              unit: timeRange === 'day' ? 'day' : 
                    timeRange === 'week' ? 'week' :
                    timeRange === 'month' ? 'month' : 'month',
              displayFormats: {
                day: 'MM-dd',
                week: 'MM-dd', 
                month: 'yyyy-MM',
                quarter: 'yyyy-QQQ',
                year: 'yyyy'
              }
            },
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 11
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              font: {
                size: 11
              },
              callback: (value) => {
                return '¥' + value.toLocaleString();
              }
            }
          }
        },
        onClick: (event, elements) => {
          if (elements.length > 0 && onPointClick) {
            const element = elements[0];
            const datasetIndex = element.datasetIndex;
            const dataIndex = element.index;
            const dataset = datasets[datasetIndex];
            const series = dataset.label;
            
            const point = aggregateData.find(
              d => d.series === series && 
                   new Date(d.timestamp).getTime() === dataset.data[dataIndex].x.getTime()
            );
            
            if (point) {
              onPointClick(point);
            }
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
  }, [aggregateData, timeRange, showLegend, enableZoom, onPointClick, onRangeChange, loading]);

  if (loading) {
    return (
      <div className="trend-chart-loading" style={{ height }}>
        <div className="spinner"></div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="trend-chart-container" style={{ position: 'relative' }}>
      <div className="trend-chart-toolbar">
        <button onClick={exportToPNG} className="export-btn" aria-label="导出为PNG">
          <i className="fas fa-image"></i> PNG
        </button>
        <button onClick={exportToCSV} className="export-btn" aria-label="导出为CSV">
          <i className="fas fa-file-csv"></i> CSV
        </button>
      </div>
      
      <div style={{ position: 'relative', height }}>
        <canvas 
          ref={canvasRef}
          role="img"
          aria-label="收入趋势图表"
        />
      </div>
      
      {/* 屏幕阅读器友好的表格版本 */}
      <div className="sr-only">
        <table>
          <caption>收入趋势数据表</caption>
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
export const trendChartStyles = `
.trend-chart-container {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.trend-chart-toolbar {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
  z-index: 10;
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

.trend-chart-loading {
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
`;