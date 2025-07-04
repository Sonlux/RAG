-- SQL schema for Supabase/vector DB
create table chat_history (
  id uuid primary key default uuid_generate_v4(),
  library text,
  question text,
  answer text,
  timestamp timestamptz default now(),
  pdf_name text
);
