-- 股东分红记录管理系统数据库设计
-- 与现有系统完美兼容的扩展设计

-- 1. 股东分红记录表
CREATE TABLE dividend_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基本信息
    shareholder_name VARCHAR(100) NOT NULL,          -- 股东名称（股东A/股东B）
    period_year INTEGER NOT NULL,                    -- 分红年份
    period_month INTEGER NOT NULL,                   -- 分红月份
    
    -- 分红金额信息
    calculated_profit FLOAT NOT NULL,                -- 系统计算应分利润
    actual_dividend FLOAT NOT NULL,                  -- 实际分红金额
    dividend_date DATE NOT NULL,                     -- 分红日期
    
    -- 分红状态
    status VARCHAR(20) DEFAULT 'pending',            -- pending/paid/cancelled
    payment_method VARCHAR(50),                      -- 支付方式（银行转账/微信/支付宝等）
    
    -- 备注信息
    remarks TEXT,                                    -- 分红备注
    operator_name VARCHAR(100),                      -- 操作员
    
    -- 快照信息（记录分红时的系统状态）
    snapshot_total_profit FLOAT,                     -- 当期总利润快照
    snapshot_profit_ratio FLOAT,                     -- 分红比例快照
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引和约束
    UNIQUE(shareholder_name, period_year, period_month, dividend_date)  -- 防止重复分红
);

-- 2. 分红汇总表（用于快速查询统计）
CREATE TABLE dividend_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 股东信息
    shareholder_name VARCHAR(100) NOT NULL,
    
    -- 汇总信息
    total_calculated FLOAT DEFAULT 0,               -- 累计应分利润
    total_paid FLOAT DEFAULT 0,                     -- 累计已分红
    total_pending FLOAT DEFAULT 0,                  -- 累计待分红
    
    -- 统计信息
    record_count INTEGER DEFAULT 0,                 -- 分红记录数
    last_dividend_date DATE,                        -- 最后分红日期
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(shareholder_name)
);

-- 3. 创建索引提升查询性能
CREATE INDEX idx_dividend_record_date ON dividend_record(dividend_date);
CREATE INDEX idx_dividend_record_period ON dividend_record(period_year, period_month);
CREATE INDEX idx_dividend_record_shareholder ON dividend_record(shareholder_name);
CREATE INDEX idx_dividend_record_status ON dividend_record(status);

-- 4. 初始化股东汇总记录
INSERT INTO dividend_summary (shareholder_name) VALUES ('股东A'), ('股东B');