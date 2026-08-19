import { afterEach, describe, expect, it, vi } from "vitest";
import { submitCopilotQuery } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("submitCopilotQuery", () => {
  it("posts the user's message to the FastAPI query endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        answer: "Yard density is the strongest modeled driver.",
        intent: "root_mechanism_analysis"
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await submitCopilotQuery("What is driving productivity?");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/query",
      expect.objectContaining({ method: "POST" })
    );
    const request = fetchMock.mock.calls[0][1] as RequestInit;
    expect(JSON.parse(String(request.body))).toEqual({
      message: "What is driving productivity?",
      terminalId: "terminal_alpha"
    });
    expect(result.answer).toContain("Yard density");
    expect(result.intent).toBe("root_mechanism_analysis");
  });

  it("surfaces an API error to the Copilot UI", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({ detail: "Intent parsing service is temporarily unavailable" })
      })
    );

    await expect(submitCopilotQuery("Explain the delay")).rejects.toThrow(
      "Intent parsing service is temporarily unavailable"
    );
  });
});
