-- init.sql
CREATE DATABASE steam_data_pipeline;
GO

USE steam_data_pipeline;
GO

-- User accounts table
CREATE TABLE user_accounts (
    id INT IDENTITY(1,1) PRIMARY KEY,
    steam_id BIGINT NOT NULL,
    name NVARCHAR(255) NOT NULL,
    created_at DATETIME2 DEFAULT SYSDATETIME(),
    paused_at DATETIME2,
    is_active BIT DEFAULT 1,
    last_log_off BIGINT DEFAULT NULL,
);
GO

-- Daily playtime table
CREATE TABLE playtime_calculated (
    id INT IDENTITY(1,1) PRIMARY KEY,
    app_id INT NOT NULL,
    playtime_delta INT NOT NULL,
    recorded_at DATETIME2 DEFAULT SYSDATETIME(),
    user_id INT NOT NULL,
    CONSTRAINT fk_user_daily FOREIGN KEY (user_id) REFERENCES user_accounts(id),
    CONSTRAINT uq_user_app_date UNIQUE (user_id, app_id, recorded_at)
);
GO

-- Forever historic playtime table
CREATE TABLE playtime_forever_historic (
   id INT IDENTITY(1,1) PRIMARY KEY,
   app_id INT NOT NULL,
   playtime_forever INT NOT NULL,
   recorded_at DATETIME2 DEFAULT SYSDATETIME(),
   user_id INT NOT NULL,
   CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES user_accounts(id)
);
GO

-- Optional indexes for faster queries
CREATE INDEX idx_daily_user_app ON playtime_calculated(user_id, app_id);
CREATE INDEX idx_forever_user_app ON playtime_forever_historic(user_id, app_id);
CREATE INDEX idx_user_accounts_steam_id ON user_accounts (steam_id);
GO


-- Enable advanced options
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;

-- Enable CLR
EXEC sp_configure 'clr enabled', 1;
RECONFIGURE;
