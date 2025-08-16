import { NextResponse } from 'next/server';

export async function GET() {
  const manifest = {
    accountAssociation: {
      header: "eyJmaWQiOjEsInR5cGUiOiJjdXN0b2R5Iiwia2V5IjoiMHhkNDJmMjU3OGZlNzI5ZGY0ZjU4YzI2YzNkMzc5NzE4NzE5YzQyNzM5In0",
      payload: "eyJkb21haW4iOiJmaXRhZ2VudC5hcHAifQ",
      signature: "MHg4ZjNhNzE5YjU4ZjI5ZGY0ZjU4YzI2YzNkMzc5NzE4NzE5YzQyNzM5"
    },
    frame: {
      version: "1",
      name: process.env.NEXT_PUBLIC_ONCHAINKIT_PROJECT_NAME || "FitAgent",
      iconUrl: `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/VeniceAI_app.webp`,
      splashImageUrl: `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/VeniceAI_splash.png`,
      splashBackgroundColor: "#1a1a1a",
      homeUrl: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
      webhookUrl: `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/api/webhook`,
    },
    noindex: process.env.NODE_ENV === 'development'
  };

  return NextResponse.json(manifest);
}