-- SQL schema for Supabase/vector DB
create table chat_history (
  id uuid primary key default uuid_generate_v4(),
  chat_id text, -- unique session id for each chat
  library text,
  question text,
  answer text,
  timestamp timestamptz default now(),
  pdf_name text
);
