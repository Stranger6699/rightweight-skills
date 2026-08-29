import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const skillsDir = path.join(root, "skills");
const bootstrapPath = path.join(skillsDir, "using-rightweight", "SKILL.md");
let cached;

function bootstrap() {
  if (cached !== undefined) return cached;
  try {
    const raw = fs.readFileSync(bootstrapPath, "utf8");
    const body = raw.replace(/^---\n[\s\S]*?\n---\n/, "").trim();
    const mapping = fs.readFileSync(path.join(skillsDir, "using-rightweight", "references", "opencode-tools.md"), "utf8");
    cached = `<RIGHTWEIGHT-BOOTSTRAP>\nThe Rightweight bootstrap is already loaded for this session. Do not load using-rightweight again.\n\n${body}\n\n${mapping}\n</RIGHTWEIGHT-BOOTSTRAP>`;
  } catch {
    cached = null;
  }
  return cached;
}

export const RightweightPlugin = async () => ({
  config: async (config) => {
    config.skills ??= {};
    config.skills.paths ??= [];
    if (!config.skills.paths.includes(skillsDir)) config.skills.paths.push(skillsDir);
  },
  "experimental.chat.messages.transform": async (_input, output) => {
    const text = bootstrap();
    if (!text || !output.messages?.length) return;
    const firstUser = output.messages.find((message) => message.info?.role === "user");
    if (!firstUser?.parts?.length) return;
    if (firstUser.parts.some((part) => part.type === "text" && part.text.includes("<RIGHTWEIGHT-BOOTSTRAP>"))) return;
    const ref = firstUser.parts[0];
    firstUser.parts.unshift({ ...ref, type: "text", text });
  },
});

export default RightweightPlugin;
