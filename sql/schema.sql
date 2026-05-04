-- Database Schema for Global Patent Intelligence Data Pipeline

DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS patents;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;

CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    filing_date DATE,
    year INTEGER,
    classification TEXT
);

CREATE TABLE inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT
);

CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patent_id TEXT NOT NULL,
    inventor_id TEXT,
    company_id TEXT,
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
