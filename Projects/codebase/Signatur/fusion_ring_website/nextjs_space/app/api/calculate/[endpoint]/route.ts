import { NextRequest, NextResponse } from 'next/server';

const BAFE_BASE_URL =
  process.env.BAFE_BASE_URL || 'https://bafe-production.up.railway.app';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ endpoint: string }> },
) {
  const { endpoint } = await params;
  const allowed = ['bazi', 'western', 'wuxing', 'fusion', 'tst'];
  if (!allowed.includes(endpoint)) {
    return NextResponse.json({ error: 'Unknown endpoint' }, { status: 400 });
  }

  try {
    const body = await request.json();
    const res = await fetch(`${BAFE_BASE_URL}/calculate/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const rawText = await res.text();

    // Try standard JSON parse
    let data: Record<string, unknown>;
    try {
      data = JSON.parse(rawText);
    } catch {
      // Detect BAFE schema-mode (type annotations instead of values)
      if (/\b(string|float|bool|int)\b/.test(rawText)) {
        return NextResponse.json(
          { error: `BAFE ${endpoint} returned schema-mode response (no real data). Check BAFE_BASE_URL configuration.`, schema_mode: true },
          { status: 503 },
        );
      }
      return NextResponse.json(
        { error: `BAFE ${endpoint} returned invalid JSON` },
        { status: 502 },
      );
    }

    if (!res.ok) {
      return NextResponse.json(
        { error: (data.detail || data.title || `BAFE ${endpoint} error`) as string, status: res.status },
        { status: res.status },
      );
    }
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
