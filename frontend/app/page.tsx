"use client";

import { useState } from "react";
import Link from "next/link";
import { StoryFeed } from "@/components/StoryFeed";
import { CATEGORIES } from "@/lib/utils";
import { PenSquare, Filter } from "lucide-react";

export default function HomePage() {
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(
    undefined
  );
  const [sortBy, setSortBy] = useState<"new" | "top" | "trending">("new");
  const [showCategoryFilter, setShowCategoryFilter] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">LifeEcho</h1>
            <p className="text-sm text-gray-600">Share your story, inspire others</p>
          </div>
          <Link
            href="/post"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            <PenSquare size={18} />
            Share Story
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-8 mb-8 border border-blue-100">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">
            Every Story Matters
          </h2>
          <p className="text-gray-700 text-lg mb-4">
            Real stories from real people. Share your experiences, inspire others, and discover wisdom from the community.
          </p>
          <div className="flex flex-wrap gap-3">
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-lg text-sm text-gray-700 shadow-sm">
              <span className="text-xl">🌟</span> Inspiring Stories
            </span>
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-lg text-sm text-gray-700 shadow-sm">
              <span className="text-xl">💪</span> Real Experiences
            </span>
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-lg text-sm text-gray-700 shadow-sm">
              <span className="text-xl">🤝</span> Supportive Community
            </span>
          </div>
        </div>

        {/* Filters and Sorting */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-8 sticky top-20 z-30">
          <div className="flex flex-col gap-4">
            {/* Sort Tabs */}
            <div className="flex gap-2">
              {(["new", "top", "trending"] as const).map((sort) => (
                <button
                  key={sort}
                  onClick={() => setSortBy(sort)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors capitalize ${
                    sortBy === sort
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {sort === "new" && "New"}
                  {sort === "top" && "Top Stories"}
                  {sort === "trending" && "Trending"}
                </button>
              ))}
            </div>

            {/* Category Filter */}
            <div className="relative">
              <button
                onClick={() => setShowCategoryFilter(!showCategoryFilter)}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium w-full justify-between"
              >
                <span className="flex items-center gap-2">
                  <Filter size={18} />
                  {selectedCategory || "All Categories"}
                </span>
                <span className="text-sm">▼</span>
              </button>

              {showCategoryFilter && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-300 rounded-lg shadow-lg z-40">
                  <button
                    onClick={() => {
                      setSelectedCategory(undefined);
                      setShowCategoryFilter(false);
                    }}
                    className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 first:rounded-t-lg"
                  >
                    All Categories
                  </button>
                  {CATEGORIES.map((category) => (
                    <button
                      key={category}
                      onClick={() => {
                        setSelectedCategory(category);
                        setShowCategoryFilter(false);
                      }}
                      className={`w-full text-left px-4 py-2 hover:bg-gray-100 ${
                        selectedCategory === category
                          ? "bg-blue-50 text-blue-600 font-medium"
                          : "text-gray-700"
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Story Feed */}
        <StoryFeed category={selectedCategory} sortBy={sortBy} />
      </main>
    </div>
  );
}
