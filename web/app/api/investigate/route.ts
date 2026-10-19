export async function POST(request: Request) {
  const body = await request.json();

  const response = await fetch("http://127.0.0.1:8000/investigate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      device_id: body.device_id ?? body.deviceId ?? null,
      question: body.question,
      previous_response_id: body.previous_response_id ?? null,
    }),
  });

  if (!response.ok) {
    return new Response("Investigation request failed.", {
      status: response.status,
    });
  }

  if (!response.body) {
    return new Response("The investigation stream was unavailable.", {
      status: 502,
    });
  }

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
    },
  });
}
