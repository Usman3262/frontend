import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function DELETE(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const storyId = searchParams.get("id");
    const anonymousNumber = searchParams.get("anon_num");
    const password = searchParams.get("password");

    if (!storyId || !anonymousNumber || !password) {
      return NextResponse.json(
        { message: "Missing required parameters" },
        { status: 400 }
      );
    }

    const response = await fetch(
      `${API_BASE_URL}/stories/${storyId}?anon_num=${encodeURIComponent(anonymousNumber)}&password=${encodeURIComponent(password)}`,
      {
        method: "DELETE",
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      return NextResponse.json(
        { message: error.detail || "Failed to delete story" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Delete story error:", error);
    return NextResponse.json(
      { message: "Internal server error" },
      { status: 500 }
    );
  }
}
