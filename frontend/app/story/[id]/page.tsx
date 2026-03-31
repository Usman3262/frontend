"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { storyApi } from "@/lib/api";
import { formatDate, REACTION_TYPES } from "@/lib/utils";
import { ArrowLeft, Heart, Trash2, Loader } from "lucide-react";

interface StoryDetail {
  id: number;
  content: string;
  category?: string;
  summary?: string;
  lessons?: string;
  created_at: string;
  view_count: number;
  reactions_count?: number;
  reaction_counts?: {
    Relatable: number;
    Inspired: number;
    StayStrong: number;
    Helpful: number;
  };
  reaction_percentages?: {
    Relatable: number;
    Inspired: number;
    StayStrong: number;
    Helpful: number;
  };
}

export default function StoryDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const router = useRouter();
  const storyId = parseInt(params.id);
  const [story, setStory] = useState<StoryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteForm, setDeleteForm] = useState({
    anonymous_number: "",
    password: "",
  });
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const [selectedReaction, setSelectedReaction] = useState<string | null>(null);
  const [isReacting, setIsReacting] = useState(false);

  useEffect(() => {
    const loadStory = async () => {
      try {
        const data = await storyApi.getStory(storyId);
        setStory(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load story"
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadStory();
  }, [storyId]);

  const handleDeleteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsDeleting(true);
    setDeleteError("");

    try {
      const response = await fetch(
        `/api/delete-story?id=${storyId}&anon_num=${encodeURIComponent(deleteForm.anonymous_number)}&password=${encodeURIComponent(deleteForm.password)}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        router.push("/");
      } else {
        const error = await response.json();
        setDeleteError(error.message || "Failed to delete story");
      }
    } catch (error) {
      setDeleteError(
        error instanceof Error ? error.message : "Failed to delete story"
      );
    } finally {
      setIsDeleting(false);
    }
  };

  const handleAddReaction = async (reactionType: string) => {
    if (selectedReaction === reactionType) {
      setSelectedReaction(null);
    } else {
      setSelectedReaction(reactionType);
      setIsReacting(true);

      try {
        await storyApi.addReaction(storyId, reactionType);
        // Reload story to get updated reaction counts
        const data = await storyApi.getStory(storyId);
        setStory(data);
      } catch (error) {
        console.error("Failed to add reaction:", error);
      } finally {
        setIsReacting(false);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader size={32} className="animate-spin text-gray-400" />
      </div>
    );
  }

  if (error || !story) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{error || "Story not found"}</p>
          <Link href="/" className="text-blue-600 hover:text-blue-700">
            ← Back to Feed
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft size={20} className="text-gray-600" />
          </button>
          <h1 className="text-xl font-bold text-gray-900">Story</h1>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <article className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-8">
            {/* Header */}
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                {story.category && (
                  <span className="inline-block px-3 py-1 text-sm font-medium text-blue-700 bg-blue-50 rounded-full mb-3">
                    {story.category}
                  </span>
                )}
                <div className="flex gap-4 text-sm text-gray-600">
                  <span>{formatDate(story.created_at)}</span>
                  <span>{story.view_count} views</span>
                </div>
              </div>
              <button
                onClick={() => setShowDeleteModal(true)}
                className="text-gray-400 hover:text-red-600 transition-colors p-2 hover:bg-red-50 rounded"
                title="Delete story"
              >
                <Trash2 size={20} />
              </button>
            </div>

            {/* Content */}
            <div className="prose prose-sm max-w-none mb-8">
              <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">
                {story.content}
              </p>
            </div>

            {/* Summary */}
            {story.summary && (
              <div className="mb-6 p-4 bg-amber-50 border-l-4 border-amber-300 rounded">
                <p className="text-sm font-medium text-amber-900 mb-2">Summary</p>
                <p className="text-sm text-amber-800">{story.summary}</p>
              </div>
            )}

            {/* Lessons */}
            {story.lessons && (
              <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-300 rounded">
                <p className="text-sm font-medium text-green-900 mb-2">
                  Key Lessons
                </p>
                <p className="text-sm text-green-800">{story.lessons}</p>
              </div>
            )}

            {/* Reactions */}
            <div className="border-t border-gray-200 pt-6">
              <p className="text-sm font-medium text-gray-900 mb-4">
                How did this story impact you?
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {REACTION_TYPES.map((type) => (
                  <button
                    key={type}
                    onClick={() => handleAddReaction(type)}
                    disabled={isReacting}
                    className={`py-3 px-4 rounded-lg font-medium transition-all ${
                      selectedReaction === type
                        ? "bg-red-600 text-white scale-105"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    } disabled:opacity-50`}
                  >
                    <span className="flex items-center justify-center gap-2">
                      <Heart size={16} fill={selectedReaction === type ? "currentColor" : "none"} />
                      {type}
                    </span>
                  </button>
                ))}
              </div>

              {/* Reaction Breakdown */}
              {story.reaction_counts && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-900 mb-3">
                    Community Response
                  </p>
                  <div className="space-y-2">
                    {REACTION_TYPES.map((type) => {
                      const count =
                        story.reaction_counts?.[type as keyof typeof story.reaction_counts] || 0;
                      const percentage =
                        story.reaction_percentages?.[type as keyof typeof story.reaction_percentages] || 0;
                      return (
                        <div key={type}>
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm text-gray-700">{type}</span>
                            <span className="text-sm font-medium text-gray-900">
                              {count} ({percentage}%)
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </article>
      </main>

      {/* Delete Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-lg max-w-sm w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Delete Story?
            </h3>
            <p className="text-gray-600 mb-6">
              This action cannot be undone. Enter your credentials to confirm.
            </p>

            <form onSubmit={handleDeleteSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Anonymous Number
                </label>
                <input
                  type="text"
                  placeholder="#4821"
                  value={deleteForm.anonymous_number}
                  onChange={(e) =>
                    setDeleteForm({
                      ...deleteForm,
                      anonymous_number: e.target.value,
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={deleteForm.password}
                  onChange={(e) =>
                    setDeleteForm({ ...deleteForm, password: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              {deleteError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                  {deleteError}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowDeleteModal(false)}
                  disabled={isDeleting}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isDeleting}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {isDeleting ? "Deleting..." : "Delete"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
