import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const extensionDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(extensionDir, "../..");
const skillsDir = resolve(root, "skills");
const bootstrapPath = resolve(skillsDir, "using-rightweight", "SKILL.md");
const marker = "rightweight bootstrap for pi";
let cached: string | null | undefined;

export default function rightweightPiExtension(pi: ExtensionAPI) {
  let inject = true;
  pi.on("resources_discover", async () => ({ skillPaths: [skillsDir] }));
  pi.on("session_start", async () => { inject = true; });
  pi.on("session_compact", async () => { inject = true; });
  pi.on("agent_end", async () => { inject = false; });
  pi.on("context", async (event) => {
    if (!inject || event.messages.some((message) => contains(message, marker))) return;
    const text = getBootstrap();
    if (!text) return;
    const message = { role: "user" as const, content: [{ type: "text" as const, text }], timestamp: Date.now() };
    return { messages: [message, ...event.messages] };
  });
}

function getBootstrap(): string | null {
  if (cached !== undefined) return cached;
  try {
    const body = readFileSync(bootstrapPath, "utf8").replace(/^---\n[\s\S]*?\n---\n/, "").trim();
    const mapping = readFileSync(resolve(skillsDir, "using-rightweight", "references", "pi-tools.md"), "utf8");
    cached = `<RIGHTWEIGHT-BOOTSTRAP>\n${marker}\n\n${body}\n\n${mapping}\n</RIGHTWEIGHT-BOOTSTRAP>`;
  } catch { cached = null; }
  return cached;
}

function contains(message: unknown, markerText: string): boolean {
  const content = (message as { content?: unknown }).content;
  if (typeof content === "string") return content.includes(markerText);
  if (!Array.isArray(content)) return false;
  return content.some((part) => part && typeof part === "object" && (part as { text?: unknown }).text?.toString().includes(markerText));
}
