-- RadarMarca SaaS MVP schema

create extension if not exists pgcrypto;

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text unique,
  full_name text,
  avatar_url text,
  created_at timestamptz not null default now()
);

create table if not exists workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  owner_user_id uuid not null references profiles(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table if not exists brands (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  name text not null,
  primary_domain text not null,
  industry text,
  goal text check (goal in ('fraud','impersonation','visibility')),
  created_at timestamptz not null default now()
);

create table if not exists brand_domains (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid not null references brands(id) on delete cascade,
  domain text not null,
  kind text not null default 'legitimate' check (kind in ('legitimate','whitelist')),
  created_at timestamptz not null default now()
);

create table if not exists scans (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid not null references brands(id) on delete cascade,
  status text not null default 'queued' check (status in ('queued','running','completed','failed')),
  source text not null default 'manual' check (source in ('manual','scheduled','trial')),
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists findings (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid not null references scans(id) on delete cascade,
  domain text not null,
  risk_score integer not null default 0,
  similarity_score numeric(5,4),
  dns_resolves boolean not null default false,
  http_reachable boolean not null default false,
  notes jsonb not null default '[]'::jsonb,
  source_tags jsonb not null default '[]'::jsonb,
  title text,
  fingerprint text,
  created_at timestamptz not null default now()
);

create table if not exists subscriptions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  provider text not null default 'stripe',
  provider_customer_id text,
  provider_subscription_id text,
  status text not null default 'trialing' check (status in ('trialing','active','past_due','canceled')),
  trial_ends_at timestamptz,
  current_period_ends_at timestamptz,
  created_at timestamptz not null default now()
);

-- Minimal RLS notes:
-- 1. each authenticated user should only read/write their own profile
-- 2. each workspace owner should only access their workspace, brands, scans and findings
-- 3. service role may insert scan/findings from backend jobs
