-- Migration for RSC Features (Discovery Swiping & Mark as Done)

-- 1. Create Swipes Table
CREATE TABLE IF NOT EXISTS public.swipes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    place_id TEXT NOT NULL,
    place_data JSONB,
    action TEXT CHECK (action IN ('like', 'dislike')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id, place_id)
);

-- Enable RLS for Swipes
ALTER TABLE public.swipes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can insert their own swipes." 
ON public.swipes FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own swipes." 
ON public.swipes FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own swipes."
ON public.swipes FOR UPDATE
USING (auth.uid() = user_id);


-- 2. Create Visited Places Table
CREATE TABLE IF NOT EXISTS public.visited_places (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    place_id TEXT NOT NULL,
    place_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id, place_id)
);

-- Enable RLS for Visited Places
ALTER TABLE public.visited_places ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can insert their own visited places." 
ON public.visited_places FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own visited places." 
ON public.visited_places FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own visited places."
ON public.visited_places FOR DELETE
USING (auth.uid() = user_id);
