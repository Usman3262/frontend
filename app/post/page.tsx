"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { storyApi } from "@/lib/api";
import { CATEGORIES, generateAnonymousNumber, generateSecurePassword, copyToClipboard } from "@/lib/utils";
import { ArrowLeft, Copy, RefreshCw } from "lucide-react";

export default function PostStoryPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    content: "",
    category: "",
    image_url: "",
    anonymous_number: generateAnonymousNumber(),
    password: generateSecurePassword(),
    useExisting: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showCredentials, setShowCredentials] = useState(false);

  const handleGenerateCredentials = () => {
    setFormData({
      ...formData,
      anonymous_number: generateAnonymousNumber(),
      password: generateSecurePassword(),
    });
  };

  const handleCopyToClipboard = (text: string, type: string) => {
    copyToClipboard(text).then(() => {
      alert(`${type} copied to clipboard!`);
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (!formData.content.trim()) {
        throw new Error("Story content cannot be empty");
      }

      if (formData.content.length < 10) {
        throw new Error("Story must be at least 10 characters");
      }

      if (formData.content.length > 2000) {
        throw new Error("Story cannot exceed 2000 characters");
      }

      const response = await storyApi.postStory({
        content: formData.content,
        category: formData.category || undefined,
        image_url: formData.image_url || undefined,
        ...(formData.useExisting && {
          anonymous_number: formData.anonymous_number,
          password: formData.password,
        }),
      });

      setSuccess(true);

      // Show success message before redirecting
      setTimeout(() => {
        router.push("/");
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to post story");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link
            href="/"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft size={20} className="text-gray-600" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Share Your Story</h1>
            <p className="text-sm text-gray-600">Your story can inspire someone</p>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        {success && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 mb-6 flex items-center gap-3">
            <span className="text-2xl">✓</span>
            <div>
              <p className="font-medium">Story posted successfully!</p>
              <p className="text-sm">Redirecting to home...</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 space-y-6">
          {/* Story Content */}
          <div>
            <label className="block text-sm font-bold text-gray-900 mb-3">
              Your Story
              <span className="text-red-600">*</span>
            </label>
            <textarea
              value={formData.content}
              onChange={(e) =>
                setFormData({ ...formData, content: e.target.value })
              }
              placeholder="Share your story here... (10-2000 characters)"
              rows={10}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              required
              minLength={10}
              maxLength={2000}
            />
            <div className="mt-2 flex justify-between items-center">
              <p className="text-xs text-gray-500">
                {formData.content.length} / 2000 characters
              </p>
              {formData.content.length < 10 && (
                <p className="text-xs text-yellow-600">
                  Minimum 10 characters required
                </p>
              )}
            </div>
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-bold text-gray-900 mb-3">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) =>
                setFormData({ ...formData, category: e.target.value })
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select a category</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Media URL */}
          <div>
            <label className="block text-sm font-bold text-gray-900 mb-3">
              Image URL (optional)
            </label>
            <input
              type="url"
              value={formData.image_url}
              onChange={(e) =>
                setFormData({ ...formData, image_url: e.target.value })
              }
              placeholder="https://example.com/image.jpg"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Provide a direct URL to an image
            </p>
          </div>

          {/* Credentials Section */}
          <div className="border-t border-gray-200 pt-6">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.useExisting}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    useExisting: e.target.checked,
                  })
                }
                className="w-4 h-4 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-900">
                Use existing account
              </span>
            </label>

            {!formData.useExisting ? (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm font-medium text-blue-900 mb-3">
                  New Account Generated
                </p>
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-blue-700 font-medium mb-1">
                      Anonymous Number
                    </p>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={formData.anonymous_number}
                        readOnly
                        className="flex-1 px-3 py-2 bg-white border border-blue-300 rounded text-sm font-mono"
                      />
                      <button
                        type="button"
                        onClick={() =>
                          handleCopyToClipboard(
                            formData.anonymous_number,
                            "Number"
                          )
                        }
                        className="px-3 py-2 bg-white border border-blue-300 rounded hover:bg-blue-50 transition-colors"
                      >
                        <Copy size={16} className="text-blue-600" />
                      </button>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-blue-700 font-medium mb-1">
                      Password
                    </p>
                    <div className="flex gap-2">
                      <input
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        readOnly
                        className="flex-1 px-3 py-2 bg-white border border-blue-300 rounded text-sm font-mono"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="px-3 py-2 bg-white border border-blue-300 rounded hover:bg-blue-50 transition-colors"
                      >
                        {showPassword ? "Hide" : "Show"}
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          handleCopyToClipboard(formData.password, "Password")
                        }
                        className="px-3 py-2 bg-white border border-blue-300 rounded hover:bg-blue-50 transition-colors"
                      >
                        <Copy size={16} className="text-blue-600" />
                      </button>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleGenerateCredentials}
                    className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    <RefreshCw size={14} />
                    Generate New Credentials
                  </button>

                  <p className="text-xs text-blue-800 mt-2 bg-white p-2 rounded border border-blue-300">
                    ⚠️ Save these credentials securely. You'll need them to delete or react to stories.
                  </p>
                </div>
              </div>
            ) : (
              <div className="mt-4 space-y-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Anonymous Number
                  </label>
                  <input
                    type="text"
                    value={formData.anonymous_number}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        anonymous_number: e.target.value,
                      })
                    }
                    placeholder="#4821"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={(e) =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="mt-2 text-sm text-blue-600 hover:text-blue-700"
                  >
                    {showPassword ? "Hide" : "Show"} password
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-3 pt-6 border-t border-gray-200">
            <Link
              href="/"
              className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors text-center"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={isLoading || formData.content.length < 10}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Posting..." : "Post Story"}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
