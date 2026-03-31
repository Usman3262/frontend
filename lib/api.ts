const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

async function apiCall<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const config: FetchOptions = {
    ...options,
    headers,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// Story API calls
export const storyApi = {
  getStories: (params?: {
    category?: string;
    search_text?: string;
    sort_by?: "new" | "top" | "trending";
    limit?: number;
    offset?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.append("category", params.category);
    if (params?.search_text) queryParams.append("search_text", params.search_text);
    if (params?.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.offset) queryParams.append("offset", params.offset.toString());

    const query = queryParams.toString();
    return apiCall<any>(`/stories${query ? `?${query}` : ""}`);
  },

  getStory: (storyId: number) =>
    apiCall<any>(`/stories/${storyId}`),

  postStory: (data: {
    content: string;
    category?: string;
    image_url?: string;
    anonymous_number?: string;
    password?: string;
  }) =>
    apiCall<any>("/stories/post-story", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteStory: (storyId: number, anonymousNumber: string, password: string) =>
    apiCall<any>(`/stories/${storyId}?anon_num=${encodeURIComponent(anonymousNumber)}&password=${encodeURIComponent(password)}`, {
      method: "DELETE",
    }),
};

// Reaction API calls
export const reactionApi = {
  addReaction: (storyId: number, reactionType: string) =>
    apiCall<any>("/reactions", {
      method: "POST",
      body: JSON.stringify({
        story_id: storyId,
        reaction_type: reactionType,
      }),
    }),

  addAuthenticatedReaction: (
    storyId: number,
    reactionType: string,
    anonymousNumber: string,
    password: string
  ) =>
    apiCall<any>("/reactions/react", {
      method: "POST",
      body: JSON.stringify({
        story_id: storyId,
        reaction_type: reactionType,
        anonymous_number: anonymousNumber,
        password: password,
      }),
    }),

  getReactions: (storyId: number) =>
    apiCall<any>(`/reactions/${storyId}`),

  getReactionBreakdown: (storyId: number) =>
    apiCall<any>(`/reactions/${storyId}/breakdown`),
};
