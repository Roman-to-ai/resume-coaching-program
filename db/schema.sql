-- CareerLens 数据库结构
-- 执行：mysql -uroot -p123456 < db/schema.sql  （或先 CREATE DATABASE careerlens）

CREATE DATABASE IF NOT EXISTS careerlens
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE careerlens;

-- 岗位表（JD 数据，来自 Java-JD-data/*_details.json）
CREATE TABLE IF NOT EXISTS jobs (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  job_id         VARCHAR(128) NOT NULL UNIQUE COMMENT 'boss job_id',
  title          VARCHAR(255) NOT NULL,
  company        VARCHAR(255),
  salary         VARCHAR(64),
  location       VARCHAR(255),
  experience     VARCHAR(32),
  degree         VARCHAR(32),
  skills         VARCHAR(1024) COMMENT '逗号分隔技能',
  description    MEDIUMTEXT COMMENT '岗位描述(HTML)',
  company_scale  VARCHAR(64),
  company_stage  VARCHAR(64),
  company_industry VARCHAR(128),
  welfare        TEXT,
  url            VARCHAR(512),
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_jobs_experience (experience),
  INDEX idx_jobs_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 匹配分析记录（可选，用于历史落库）
CREATE TABLE IF NOT EXISTS analysis_record (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  resume_text  MEDIUMTEXT,
  job_id       VARCHAR(128),
  match_score  INT,
  level        VARCHAR(16),
  result_json  JSON,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_analysis_job (job_id),
  INDEX idx_analysis_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
