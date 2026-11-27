-- Run once in Supabase SQL Editor.
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS gender TEXT
DEFAULT 'Prefer not to say';
