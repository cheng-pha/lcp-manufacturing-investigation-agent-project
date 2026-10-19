
"use client";

import { useEffect, useRef, useState } from "react";

type Message = {
  question: string;
  answer: string;
};

export default function Home() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [streamingAnswer, setStreamingAnswer] = useState("");
  const [investigationStatus, setInvestigationStatus] = useState(
    "Gathering available information..."
  );
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [previousResponseId, setPreviousResponseId] = useState<string | null>(
    null
  );
  const [messages, setMessages] = useState<Message[]>([]);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages, streamingAnswer, investigationStatus, isInvestigating]);

  const investigate = async () => {
    const currentQuestion = question.trim();

    if (!currentQuestion || isInvestigating) return;

    setIsInvestigating(true);
    setSubmittedQuestion(currentQuestion);
    setStreamingAnswer("");
    setInvestigationStatus("Analyzing your question...");
    setQuestion("");

    let receivedAnswer = "";

    try {
      const response = await fetch("/api/investigate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          device_id: null,
          question: currentQuestion,
          previous_response_id: previousResponseId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Investigation failed (${response.status})`);
      }

      if (!response.body) {
        throw new Error("The response stream was unavailable.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let receivedResponseId: string | null = null;

      while (true) {
        const { value, done } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const eventText of events) {
          const dataLine = eventText
            .split("\n")
            .find((line) => line.startsWith("data: "));

          if (!dataLine) continue;

          const payload = JSON.parse(dataLine.slice(6));

          if (payload.type === "status") {
            setInvestigationStatus(payload.message);
          } else if (payload.type === "text") {
            receivedAnswer += payload.text;
            setStreamingAnswer(receivedAnswer);
          } else if (payload.type === "done") {
            receivedResponseId = payload.response_id;
          } else if (payload.type === "error") {
            throw new Error(payload.message);
          }
        }
      }

      if (!receivedAnswer) {
        throw new Error("The agent returned an empty response.");
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          question: currentQuestion,
          answer: receivedAnswer,
        },
      ]);

      if (receivedResponseId) {
        setPreviousResponseId(receivedResponseId);
      }

      setStreamingAnswer("");
    } catch (error) {
      console.error("Investigation error:", error);

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          question: currentQuestion,
          answer: receivedAnswer
            ? `${receivedAnswer}\n\nThe response ended unexpectedly.`
            : "Sorry, the investigation failed. Please try again.",
        },
      ]);

      setStreamingAnswer("");
    } finally {
      setIsInvestigating(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#05080b] text-slate-200">
      <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-10">
        {/* Page Header */}
        <header className="mb-6 border-b border-slate-800 pb-6 sm:mb-8 sm:pb-8">
          <p className="text-sm font-medium tracking-wide text-cyan-400">
            PROJECT AI
          </p>

          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-100 sm:text-4xl">
            Medical Device Investigation
          </h1>

          <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400 sm:text-base">
            Investigate device history, manufacturing status, quality events,
            holds, scrap records, and documented procedures using an
            evidence-based AI agent.
          </p>
        </header>

        {/* Unified Chat */}
        <section className="overflow-hidden rounded-2xl border border-slate-800 bg-[#080d12] shadow-2xl shadow-black/20">
          {/* Chat Header */}
          <div className="flex items-center justify-between gap-3 border-b border-slate-800 px-5 py-4 sm:px-6">
            <div>
              <h2 className="text-sm font-semibold text-slate-100 sm:text-base">
                Chat History
              </h2>
            </div>

            <div className="flex shrink-0 items-center gap-2">
              <span
                className={`h-2 w-2 rounded-full ${
                  isInvestigating
                    ? "animate-pulse bg-cyan-400"
                    : "bg-emerald-400"
                }`}
              />
              <span className="text-xs text-slate-400">
                {isInvestigating ? "Investigating" : "Ready"}
              </span>
            </div>
          </div>

          {/* Conversation */}
          <div className="h-[520px] overflow-y-auto bg-[#05080b] px-4 py-6 sm:px-6">
            {messages.length === 0 && !isInvestigating ? (
              <div className="flex h-full items-center justify-center">
                <div className="max-w-sm text-center">
                  <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-900/70 bg-cyan-950/40">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="h-7 w-7 text-cyan-400"
                    >
                      <path d="M12 8V4H8" />
                      <rect width="16" height="12" x="4" y="8" rx="2" />
                      <path d="M2 14h2" />
                      <path d="M20 14h2" />
                      <path d="M9 13v2" />
                      <path d="M15 13v2" />
                    </svg>
                  </div>

                  <h3 className="text-lg font-medium text-slate-200">
                    What would you like to investigate?
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    Ask about a device, manufacturing lot, quality event,
                    scrap disposition, or documented procedure.
                  </p>

                  <div className="mt-5 flex flex-wrap justify-center gap-2">
                    {[
                      "What's the status of LCP-10501?",
                      "Why was LCP-10482 scrapped?",
                    ].map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => setQuestion(suggestion)}
                        className="rounded-full border border-slate-700 px-3 py-2 text-left text-xs text-slate-400 transition hover:border-cyan-700 hover:text-cyan-300"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div key={index} className="space-y-4">
                    {/* User Message */}
                    <div className="flex justify-end">
                      <div className="max-w-[90%] rounded-2xl rounded-br-md bg-cyan-500 px-4 py-3 text-sm leading-6 text-slate-950 shadow-lg shadow-cyan-950/20 sm:max-w-[80%] sm:px-5">
                        {message.question}
                      </div>
                    </div>

                    {/* Agent Message */}
                    <div className="flex justify-start">
                      <div className="max-w-[95%] rounded-2xl rounded-bl-md border border-slate-800 bg-[#0a1016] px-4 py-4 sm:max-w-[88%] sm:px-5">
                        <div className="mb-3 flex items-center gap-2">
                          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-950/70">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.7"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              className="h-4 w-4 text-cyan-400"
                            >
                              <rect
                                width="16"
                                height="12"
                                x="4"
                                y="8"
                                rx="2"
                              />
                              <path d="M12 8V4" />
                              <path d="M9 13v2" />
                              <path d="M15 13v2" />
                            </svg>
                          </div>

                          <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                            Agent
                          </span>
                          <span className="ml-auto text-xs text-slate-600">
                            {index + 1}
                          </span>
                        </div>

                        <p className="whitespace-pre-wrap text-sm leading-7 text-slate-300">
                          {message.answer}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Current Streaming Investigation */}
                {isInvestigating && (
                  <div className="space-y-4">
                    <div className="flex justify-end">
                      <div className="max-w-[90%] rounded-2xl rounded-br-md bg-cyan-500 px-4 py-3 text-sm leading-6 text-slate-950 shadow-lg shadow-cyan-950/20 sm:max-w-[80%] sm:px-5">
                        {submittedQuestion}
                      </div>
                    </div>

                    <div className="flex justify-start">
                      <div className="max-w-[95%] rounded-2xl rounded-bl-md border border-slate-800 bg-[#0a1016] px-4 py-4 sm:max-w-[88%] sm:px-5">
                        <div className="mb-3 flex items-center gap-2">
                          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-400" />
                          <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                            Agent
                          </span>
                        </div>

                        {streamingAnswer ? (
                          <div>
                            <p className="whitespace-pre-wrap text-sm leading-7 text-slate-300">
                              {streamingAnswer}
                              <span className="ml-1 inline-block h-4 w-1 animate-pulse bg-cyan-400 align-middle" />
                            </p>
                          </div>
                        ) : (
                          <div className="flex items-center gap-3 text-sm text-slate-400">
                            <span className="flex shrink-0 gap-1">
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400" />
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400 [animation-delay:150ms]" />
                              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400 [animation-delay:300ms]" />
                            </span>
                            <span>{investigationStatus}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div ref={bottomRef} />
              </div>
            )}
          </div>

          {/* Message Composer */}
          <div className="border-t border-slate-800 bg-[#080d12] p-4 sm:p-5">
            <form
              className="flex items-end gap-3"
              onSubmit={(event) => {
                event.preventDefault();
                investigate();
              }}
            >
              <div className="flex-1 rounded-xl border border-slate-700 bg-[#05080b] transition focus-within:border-cyan-700">
                <textarea
                  rows={1}
                  placeholder="Ask about a device, lot, quality event, or procedure..."
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey &&
                      !isInvestigating
                    ) {
                      event.preventDefault();
                      investigate();
                    }
                  }}
                  disabled={isInvestigating}
                  className="max-h-32 min-h-12 w-full resize-y bg-transparent px-4 py-3.5 text-sm leading-5 text-slate-200 outline-none placeholder:text-slate-600 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <button
                type="submit"
                disabled={isInvestigating || !question.trim()}
                aria-label="Send investigation question"
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-cyan-500 text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-800 disabled:text-slate-600"
              >
                {isInvestigating ? (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-5 w-5"
                  >
                    <path d="M12 19V5" />
                    <path d="m5 12 7-7 7 7" />
                  </svg>
                )}
              </button>
            </form>

            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 px-1">
              <span className="text-xs text-slate-600">
                Synthetic manufacturing data • Portfolio demonstration
              </span>
              <span className="text-xs text-slate-600">
                Enter to send · Shift+Enter for a new line
              </span>
            </div>
          </div>
        </section>

        <footer className="mt-5 text-center text-xs text-slate-700">
          AI-assisted manufacturing investigation • Source-grounded responses
        </footer>
      </div>
    </main>
  );
}
