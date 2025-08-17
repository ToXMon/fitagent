import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    
    // Basic frame interaction handler
    // In production, this would validate the frame message and handle user interactions
    console.log('Frame request body:', body);
    
    return NextResponse.json({
      type: 'frame',
      frameUrl: `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}`,
      image: `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/VeniceAI_hero.png`,
      buttons: [
        {
          label: 'Open FitAgent',
          action: 'link',
          target: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'
        }
      ]
    });
  } catch (error) {
    console.error('Frame API error:', error);
    return NextResponse.json({ error: 'Invalid frame request' }, { status: 400 });
  }
}

export async function GET() {
  // Handle GET requests for frame validation
  return NextResponse.json({ 
    message: 'FitAgent Frame API',
    version: '1.0.0'
  });
}