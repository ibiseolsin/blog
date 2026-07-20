create table if not exists public.tasks (
  id bigint generated always as identity primary key,
  title text not null,
  description text,
  is_done boolean not null default false,
  due_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.tags (
  id bigint generated always as identity primary key,
  name text not null unique
);

create table if not exists public.task_tags (
  task_id bigint not null references public.tasks(id) on delete cascade,
  tag_id bigint not null references public.tags(id) on delete cascade,
  primary key (task_id, tag_id)
);

alter table public.tasks enable row level security;
alter table public.tags enable row level security;
alter table public.task_tags enable row level security;

-- 의도적으로 정책(policy)을 하나도 추가하지 않는다.
-- 이 앱은 로그인/사용자 구분이 없는 개인용 앱이라 사용자별 정책은 의미가 없다.
-- RLS만 켜두면 anon/authenticated 키로는 기본적으로 아무 행도 읽거나 쓸 수 없고(default-deny),
-- 백엔드가 쓰는 service_role 키만 RLS를 우회해서 접근할 수 있다.
-- 즉 "허용된 접근"은 .env에만 있는 service_role 키를 가진 우리 서버뿐이다.
