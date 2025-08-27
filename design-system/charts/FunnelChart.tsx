import React, { useRef, useEffect, useState, useMemo } from 'react';
import Chart from 'chart.js/auto';
import { ChartConfiguration } from 'chart.js';

// 漏斗阶段 Schema
export interface FunnelStage {
  stage: string;
  value: number;
  percentage: number;
  conversionRate?: number; // 相对于上一阶段的转化率
  metadata?: {
    duration?: number; // 平均停留时间（天）
    dropoffReasons?: string[]; // 流失原因
    averageValue?: number; // 平均价值
    [key: string]: any;
  };
}

// 组件 Props
export interface FunnelChartProps {
  data: FunnelStage[];
  onStageClick?: (stage: FunnelStage, dropoffData?: any) => void;
  height?: number;
  loading?: boolean;
  showValues?: boolean;
  showPercentage?: boolean;
  showConversionRate?: boolean;
  orientation?: 'vertical' | 'horizontal';
  exportFileName?: string;
  colorGradient?: boolean;
}

// JSON Schema
export const FunnelDataSchema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["stage", "value", "percentage"],
    "properties": {
      "stage": {
        "type": "string",
        "description": "漏斗阶段名称"
      },
      "value": {
        "type": "number",
        "description": "该阶段的数值（客户数或金额）"
      },
      "percentage": {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "description": "相对于第一阶段的百分比"
      },
      "conversionRate": {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "description": "相对于上一阶段的转化率"
      },
      "metadata": {
        "type": "object",
        "properties": {
          "duration": {
            "type": "number",
            "description": "平均停留时间（天）"
          },
          "dropoffReasons": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "流失原因列表"
          },
          "averageValue": {
            "type": "number",
            "description": "平均价值"
          }
        }
      }
    }
  }
};

// Mock Data Generator
export const generateMockFunnelData = (): FunnelStage[] => {
  const stages = [
    { name: '咨询', baseValue: 1000, duration: 1 },
    { name: '试听预约', baseValue: 750, duration: 3 },
    { name: '试听完成', baseValue: 600, duration: 7 },
    { name: '正课报名', baseValue: 420, duration: 14 },
    { name: '续费', baseValue: 280, duration: 90 }
  ];
  
  const firstValue = stages[0].baseValue;
  
  return stages.map((stage, index) => {
    const prevValue = index > 0 ? stages[index - 1].baseValue : stage.baseValue;
    const conversionRate = index > 0 ? (stage.baseValue / prevValue * 100) : 100;
    
    return {
      stage: stage.name,
      value: stage.baseValue,
      percentage: Number((stage.baseValue / firstValue * 100).toFixed(1)),
      conversionRate: Number(conversionRate.toFixed(1)),
      metadata: {
        duration: stage.duration,
        dropoffReasons: index > 0 ? [
          '价格因素',
          '距离太远',
          '时间不合适',
          '选择其他机构'
        ].slice(0, Math.floor(Math.random() * 3) + 1) : [],
        averageValue: Math.round(5000 + Math.random() * 10000)
      }
    };
  });
};

export const FunnelChart: React.FC<FunnelChartProps> = ({
  data,
  onStageClick,
  height = 400,
  loading = false,
  showValues = true,
  showPercentage = true,
  showConversionRate = true,
  orientation = 'vertical',
  exportFileName = 'conversion-funnel',
  colorGradient = true
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);
  const [hoveredStage, setHoveredStage] = useState<number | null>(null);

  // 计算流失数据
  const dropoffData = useMemo(() => {
    return data.map((stage, index) => {
      if (index === 0) return null;
      
      const prevStage = data[index - 1];
      const dropoff = prevStage.value - stage.value;
      const dropoffRate = (dropoff / prevStage.value * 100).toFixed(1);
      
      return {
        from: prevStage.stage,
        to: stage.stage,
        dropoff,
        dropoffRate: Number(dropoffRate),
        reasons: stage.metadata?.dropoffReasons || []
      };
    }).filter(Boolean);
  }, [data]);

  // 生成颜色
  const getStageColor = (index: number, total: number) => {
    if (!colorGradient) {
      const colors = ['#4A90E2', '#52C41A', '#FF9500', '#7C3AED', '#17A2B8'];
      return colors[index % colors.length];
    }
    
    // 渐变色：从深蓝到浅蓝
    const hue = 210; // 蓝色色调
    const saturation = 70 - (index / total) * 30; // 饱和度递减
    const lightness = 45 + (index / total) * 20; // 亮度递增
    
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

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
    const headers = ['阶段', '数量', '占比(%)', '转化率(%)', '平均停留时间(天)', '平均价值'];
    const rows = data.map(stage => [
      stage.stage,
      stage.value,
      stage.percentage,
      stage.conversionRate || 100,
      stage.metadata?.duration || '',
      stage.metadata?.averageValue || ''
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

  // 自定义漏斗图绘制
  const drawFunnel = (ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
    const padding = 40;
    const width = canvas.width - padding * 2;
    const height = canvas.height - padding * 2;
    const stageHeight = height / data.length;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制每个阶段
    data.forEach((stage, index) => {
      const y = padding + index * stageHeight;
      const widthRatio = stage.value / data[0].value;
      const stageWidth = width * widthRatio;
      const x = padding + (width - stageWidth) / 2;
      
      // 绘制梯形（漏斗段）
      ctx.beginPath();
      
      if (index === 0) {
        // 第一个阶段：矩形顶部
        ctx.moveTo(x, y);
        ctx.lineTo(x + stageWidth, y);
      } else {
        // 连接上一个阶段
        const prevStage = data[index - 1];
        const prevWidthRatio = prevStage.value / data[0].value;
        const prevStageWidth = width * prevWidthRatio;
        const prevX = padding + (width - prevStageWidth) / 2;
        
        ctx.moveTo(prevX, y);
        ctx.lineTo(prevX + prevStageWidth, y);
      }
      
      // 绘制当前阶段
      const nextY = y + stageHeight;
      ctx.lineTo(x + stageWidth, nextY);
      ctx.lineTo(x, nextY);
      ctx.closePath();
      
      // 填充颜色
      ctx.fillStyle = getStageColor(index, data.length);
      ctx.fill();
      
      // 悬停效果
      if (hoveredStage === index) {
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      
      // 绘制文本
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 14px -apple-system, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      const textY = y + stageHeight / 2;
      const textX = canvas.width / 2;
      
      // 阶段名称
      ctx.fillText(stage.stage, textX, textY - 20);
      
      // 数值
      if (showValues) {
        ctx.font = '16px -apple-system, sans-serif';
        ctx.fillText(stage.value.toLocaleString(), textX, textY);
      }
      
      // 百分比
      if (showPercentage) {
        ctx.font = '12px -apple-system, sans-serif';
        ctx.fillText(`${stage.percentage}%`, textX, textY + 20);
      }
      
      // 转化率（在阶段之间）
      if (showConversionRate && index > 0) {
        ctx.save();
        ctx.fillStyle = '#666';
        ctx.font = '12px -apple-system, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(
          `↓ ${stage.conversionRate}%`,
          canvas.width - padding - 10,
          y + 10
        );
        ctx.restore();
      }
    });
  };

  useEffect(() => {
    if (!canvasRef.current || loading) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 设置画布尺寸
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // 绘制漏斗图
    drawFunnel(ctx, canvas);

    // 鼠标事件处理
    const handleMouseMove = (event: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      const padding = 40;
      const stageHeight = (rect.height - padding * 2) / data.length;
      const hoveredIndex = Math.floor((y - padding) / stageHeight);
      
      if (hoveredIndex >= 0 && hoveredIndex < data.length) {
        setHoveredStage(hoveredIndex);
        canvas.style.cursor = 'pointer';
      } else {
        setHoveredStage(null);
        canvas.style.cursor = 'default';
      }
    };

    const handleClick = (event: MouseEvent) => {
      if (hoveredStage !== null && onStageClick) {
        const stage = data[hoveredStage];
        const dropoff = hoveredStage > 0 ? dropoffData[hoveredStage - 1] : null;
        onStageClick(stage, dropoff);
      }
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('click', handleClick);

    return () => {
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('click', handleClick);
    };
  }, [data, hoveredStage, showValues, showPercentage, showConversionRate, loading, onStageClick, dropoffData]);

  // 重绘当悬停状态改变时
  useEffect(() => {
    if (!canvasRef.current) return;
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;
    
    drawFunnel(ctx, canvasRef.current);
  }, [hoveredStage]);

  if (loading) {
    return (
      <div className="funnel-chart-loading" style={{ height }}>
        <div className="spinner"></div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="funnel-chart-container">
      <div className="funnel-chart-toolbar">
        <button onClick={exportToPNG} className="export-btn" aria-label="导出为PNG">
          <i className="fas fa-image"></i> PNG
        </button>
        <button onClick={exportToCSV} className="export-btn" aria-label="导出为CSV">
          <i className="fas fa-file-csv"></i> CSV
        </button>
      </div>
      
      <div className="funnel-chart-wrapper" style={{ height }}>
        <canvas 
          ref={canvasRef}
          style={{ width: '100%', height: '100%' }}
          role="img"
          aria-label="转化漏斗图表"
        />
        
        {/* 流失分析面板 */}
        {hoveredStage !== null && hoveredStage > 0 && (
          <div className="dropoff-panel">
            <h4>流失分析</h4>
            <div className="dropoff-stats">
              <span className="dropoff-value">
                {dropoffData[hoveredStage - 1]?.dropoff.toLocaleString()} 
              </span>
              <span className="dropoff-rate">
                ({dropoffData[hoveredStage - 1]?.dropoffRate}%)
              </span>
            </div>
            {dropoffData[hoveredStage - 1]?.reasons.length > 0 && (
              <div className="dropoff-reasons">
                <p>主要原因：</p>
                <ul>
                  {dropoffData[hoveredStage - 1]?.reasons.map((reason, i) => (
                    <li key={i}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* 屏幕阅读器友好的表格版本 */}
      <div className="sr-only">
        <table>
          <caption>转化漏斗数据表</caption>
          <thead>
            <tr>
              <th>阶段</th>
              <th>数量</th>
              <th>占比</th>
              <th>转化率</th>
              <th>平均停留时间</th>
            </tr>
          </thead>
          <tbody>
            {data.map((stage, i) => (
              <tr key={i}>
                <td>{stage.stage}</td>
                <td>{stage.value.toLocaleString()}</td>
                <td>{stage.percentage}%</td>
                <td>{stage.conversionRate || 100}%</td>
                <td>{stage.metadata?.duration ? `${stage.metadata.duration}天` : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// CSS Styles
export const funnelChartStyles = `
.funnel-chart-container {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
}

.funnel-chart-toolbar {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
  z-index: 10;
}

.funnel-chart-wrapper {
  position: relative;
}

.dropoff-panel {
  position: absolute;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 16px;
  border-radius: 8px;
  min-width: 200px;
  font-size: 14px;
  pointer-events: none;
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-50%) translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateY(-50%) translateX(0);
  }
}

.dropoff-panel h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
}

.dropoff-stats {
  margin-bottom: 12px;
}

.dropoff-value {
  font-size: 20px;
  font-weight: 700;
  color: #FF6B6B;
}

.dropoff-rate {
  font-size: 14px;
  color: #FFB6B6;
  margin-left: 8px;
}

.dropoff-reasons {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.dropoff-reasons p {
  margin: 0 0 8px 0;
  font-weight: 600;
}

.dropoff-reasons ul {
  margin: 0;
  padding-left: 20px;
  list-style: disc;
}

.dropoff-reasons li {
  margin-bottom: 4px;
  font-size: 13px;
  opacity: 0.9;
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

.funnel-chart-loading {
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
  .funnel-chart-container {
    padding: 12px;
  }
  
  .funnel-chart-toolbar {
    position: static;
    margin-bottom: 12px;
    justify-content: flex-end;
  }
  
  .dropoff-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    right: auto;
    z-index: 100;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
}
`;