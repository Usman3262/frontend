"use client";

import { useState, useEffect } from "react";
import { StoryCard } from "./StoryCard";
import { storyApi } from "@/lib/api";
import { Loader } from "lucide-react";

interface Story {
  id: number;
  snippet: string;
  category?: string;
  reactions_count: number;
  summary?: string;
  lessons?: string;
  created_at: string;
  view_count: number;
}

interface StoryFeedProps {
  category?: string;
  sortBy?: "new" | "top" | "trending";
}

export function StoryFeed({ category, sortBy = "new" }: StoryFeedProps) {
  const [stories, setStories] = useState<Story[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);

  const loadStories = async (reset: boolean = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const currentOffset = reset ? 0 : offset;
      const response = await storyApi.getStories({
        category: category,
        sort_by: sortBy,
        limit: 10,
        offset: currentOffset,
      });

      const newStories = response.stories || [];
      
      setStories(
        reset ? newStories : [...stories, ...newStories]
      );

      setHasMore(newStories.length === 10);
      setOffset(currentOffset + newStories.length);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load stories"
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setStories([]);
    setOffset(0);
    setHasMore(true);
  }, [category, sortBy]);

  useEffect(() => {
    loadStories(true);
  }, [category, sortBy]);

  const handleDeleteStory = (storyId: number) => {
    setStories(stories.filter((s) => s.id !== storyId));
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {stories.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No stories yet</p>
          <p className="text-gray-400 text-sm mt-2">
            Be the first to share your story
          </p>
        </div>
      )}

      <div className="space-y-4">
        {stories.map((story) => (
          <StoryCard
            key={story.id}
            {...story}
            onDelete={handleDeleteStory}
          />
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center pt-6">
          <button
            onClick={() => loadStories()}
            disabled={isLoading}
            className="px-6 py-2 text-blue-600 font-medium border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <Loader size={16} className="animate-spin" />
                Loading...
              </span>
            ) : (
              "Load More"
            )}
          </button>
        </div>
      )}

      {isLoading && stories.length === 0 && (
        <div className="flex justify-center py-12">
          <Loader size={32} className="animate-spin text-gray-400" />
        </div>
      )}
    </div>
  );
}
