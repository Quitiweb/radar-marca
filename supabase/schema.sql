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

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name, avatar_url)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'name'),
    new.raw_user_meta_data->>'avatar_url'
  )
  on conflict (id) do update set
    email = excluded.email,
    full_name = coalesce(excluded.full_name, public.profiles.full_name),
    avatar_url = coalesce(excluded.avatar_url, public.profiles.avatar_url);

  insert into public.workspaces (name, owner_user_id)
  select coalesce(new.raw_user_meta_data->>'full_name', split_part(coalesce(new.email, 'workspace'), '@', 1)), new.id
  where not exists (
    select 1 from public.workspaces where owner_user_id = new.id
  );

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

alter table profiles enable row level security;
alter table workspaces enable row level security;
alter table brands enable row level security;
alter table brand_domains enable row level security;
alter table scans enable row level security;
alter table findings enable row level security;
alter table subscriptions enable row level security;

grant usage on schema public to anon, authenticated;
grant select, insert, update on table profiles to authenticated;
grant select, insert, update on table workspaces to authenticated;
grant select, insert, update, delete on table brands to authenticated;
grant select, insert, update, delete on table brand_domains to authenticated;
grant select on table scans to authenticated;
grant select on table findings to authenticated;
grant select on table subscriptions to authenticated;

create policy "profiles_select_own" on profiles
  for select to authenticated
  using (auth.uid() = id);

create policy "profiles_update_own" on profiles
  for update to authenticated
  using (auth.uid() = id)
  with check (auth.uid() = id);

create policy "profiles_insert_own" on profiles
  for insert to authenticated
  with check (auth.uid() = id);

create policy "workspaces_select_own" on workspaces
  for select to authenticated
  using (owner_user_id = auth.uid());

create policy "workspaces_insert_own" on workspaces
  for insert to authenticated
  with check (owner_user_id = auth.uid());

create policy "workspaces_update_own" on workspaces
  for update to authenticated
  using (owner_user_id = auth.uid())
  with check (owner_user_id = auth.uid());

create policy "brands_manage_owned_workspace" on brands
  for all to authenticated
  using (
    exists (
      select 1 from workspaces w
      where w.id = brands.workspace_id and w.owner_user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1 from workspaces w
      where w.id = brands.workspace_id and w.owner_user_id = auth.uid()
    )
  );

create policy "brand_domains_manage_owned_brand" on brand_domains
  for all to authenticated
  using (
    exists (
      select 1
      from brands b
      join workspaces w on w.id = b.workspace_id
      where b.id = brand_domains.brand_id and w.owner_user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1
      from brands b
      join workspaces w on w.id = b.workspace_id
      where b.id = brand_domains.brand_id and w.owner_user_id = auth.uid()
    )
  );

create policy "scans_select_owned_brand" on scans
  for select to authenticated
  using (
    exists (
      select 1
      from brands b
      join workspaces w on w.id = b.workspace_id
      where b.id = scans.brand_id and w.owner_user_id = auth.uid()
    )
  );

create policy "findings_select_owned_scan" on findings
  for select to authenticated
  using (
    exists (
      select 1
      from scans s
      join brands b on b.id = s.brand_id
      join workspaces w on w.id = b.workspace_id
      where s.id = findings.scan_id and w.owner_user_id = auth.uid()
    )
  );

create policy "subscriptions_select_owned_workspace" on subscriptions
  for select to authenticated
  using (
    exists (
      select 1 from workspaces w
      where w.id = subscriptions.workspace_id and w.owner_user_id = auth.uid()
    )
  );
