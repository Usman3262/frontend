"use client";

import { useState } from "react";
import Link from "next/link";
import { reactionApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Heart, Share2, Trash2 } from "lucide-react";

interface StoryCardProps {
  id: number;
  snippet: string;
  category?: string;
  reactions_count: number;
  summary?: string;
  lessons?: string;
  created_at: string;
  view_count: number;
  onDelete?: (storyId: number) => void;
}

export function StoryCard({
  id,
  snippet,
  category,
  reactions_count,
  summary,
  lessons,
  created_at,
  view_count,
  onDelete,
}: StoryCardProps) {
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteForm, setDeleteForm] = useState({
    anonymous_number: "",
    password: "",
  });
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const handleDeleteClick = () => {
    setShowDeleteModal(true);
    setDeleteError("");
  };

  const handleDeleteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsDeleting(true);
    setDeleteError("");

    try {
      const response = await fetch(
        `/api/delete-story?id=${id}&anon_num=${encodeURIComponent(deleteForm.anonymous_number)}&password=${encodeURIComponent(deleteForm.password)}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        setShowDeleteModal(false);
        setDeleteForm({ anonymous_number: "", password: "" });
        onDelete?.(id);
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

  return (
    <>
      <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
        <div className="p-6">
          {/* Card Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              {category && (
                <span className="inline-block px-3 py-1 text-sm font-medium text-blue-700 bg-blue-50 rounded-full mb-2">
                  {category}
                </span>
              )}
              <p className="text-sm text-gray-500">{formatDate(created_at)}</p>
            </div>
            <button
              onClick={handleDeleteClick}
              className="text-gray-400 hover:text-red-600 transition-colors p-2 hover:bg-red-50 rounded"
              title="Delete story"
            >
              <Trash2 size={18} />
            </button>
          </div>

          {/* Story Snippet */}
          <Link href={`/story/${id}`}>
            <p className="text-gray-800 line-clamp-3 hover:text-blue-600 transition-colors cursor-pointer mb-4">
              {snippet}
            </p>
          </Link>

          {/* Summary */}
          {summary && (
            <div className="mb-4 p-3 bg-amber-50 border-l-4 border-amber-300 rounded">
              <p className="text-sm text-amber-900 font-medium">Summary</p>
              <p className="text-sm text-amber-800 mt-1 line-clamp-2">
                {summary}
              </p>
            </div>
          )}

          {/* Lessons */}
          {lessons && (
            <div className="mb-4 p-3 bg-green-50 border-l-4 border-green-300 rounded">
              <p className="text-sm text-green-900 font-medium">Key Lessons</p>
              <p className="text-sm text-green-800 mt-1 line-clamp-2">
                {lessons}
              </p>
            </div>
          )}

          {/* Card Footer */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <div className="flex items-center gap-4 text-gray-600">
              <div className="flex items-center gap-2">
                <Heart size={18} className="text-red-500" />
                <span className="text-sm font-medium">{reactions_count}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">
                  {view_count} {view_count === 1 ? "view" : "views"}
                </span>
              </div>
            </div>
            <button className="text-gray-500 hover:text-blue-600 transition-colors p-2">
              <Share2 size={18} />
            </button>
          </div>
        </div>
      </article>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-lg max-w-sm w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Delete Story?
            </h3>
            <p className="text-gray-600 mb-6">
              This action cannot be undone. Please enter your credentials to confirm deletion.
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
    </>
  );
}
