import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    
    // Handle Farcaster webhook events
    // This would process notifications about frame interactions, user actions, etc.
    
    console.log('Webhook received:', body);
    
    // Validate webhook signature in production
    // Process different event types (frame_added, frame_removed, etc.)
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Webhook error:', error);
    return NextResponse.json({ error: 'Webhook processing failed' }, { status: 500 });
  }
}

export async function GET() {
  // Health check for webhook endpoint
  return NextResponse.json({ 
    status: 'active',
    service: 'FitAgent Webhook Handler'
  });
}