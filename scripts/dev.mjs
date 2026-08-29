import { existsSync, readFileSync } from "node:fs";
import { dirname, delimiter, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

function loadEnvFile() {
  const envPath = join(repoRoot, ".env");
  if (!existsSync(envPath)) {
    return;
  }

  for (const rawLine of readFileSync(envPath, "utf8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) {
      continue;
    }

    const separator = line.indexOf("=");
    if (separator <= 0) {
      continue;
    }

    const name = line.slice(0, separator).trim();
    let value = line.slice(separator + 1).trim();
    if (
      value.length >= 2 &&
      ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'")))
    ) {
      value = value.slice(1, -1);
    }

    if (!(name in process.env)) {
      process.env[name] = value;
    }
  }
}

function appendPythonPath(environment) {
  const pythonPaths = [
    "apps/api/src",
    "packages/rag-engine/src",
    "packages/causal-engine/src",
    "packages/llm-orchestrator/src",
    "packages/shared-domain/src",
    "packages/data-connectors/src",
  ].map((relativePath) => join(repoRoot, relativePath));

  environment.PYTHONPATH = [
    ...pythonPaths,
    ...(environment.PYTHONPATH ? [environment.PYTHONPATH] : []),
  ].join(delimiter);
}

function startProcess(command, args, environment) {
  return spawn(command, args, {
    cwd: repoRoot,
    env: environment,
    stdio: "inherit",
    windowsHide: false,
  });
}

loadEnvFile();

if (
  (process.env.INTENT_PARSER_MODE ?? "claude").toLowerCase() === "claude" &&
  !process.env.ANTHROPIC_API_KEY?.trim()
) {
  console.error("ANTHROPIC_API_KEY is required when INTENT_PARSER_MODE=claude.");
  console.error("Add it to the repository .env file or set INTENT_PARSER_MODE=mock.");
  process.exit(1);
}

const childEnvironment = { ...process.env };
appendPythonPath(childEnvironment);

const pythonCommand = process.env.PYTHON ?? (process.platform === "win32" ? "python" : "python3");
const npmCommand = process.platform === "win32" ? "cmd.exe" : "npm";
const npmArguments =
  process.platform === "win32"
    ? ["/d", "/s", "/c", "npm.cmd --workspace apps/web run dev"]
    : ["--workspace", "apps/web", "run", "dev"];
const apiProcess = startProcess(
  pythonCommand,
  [
    "-m",
    "uvicorn",
    "api.main:app",
    "--host",
    process.env.API_HOST ?? "0.0.0.0",
    "--port",
    process.env.API_PORT ?? "8000",
  ],
  childEnvironment,
);
const webProcess = startProcess(npmCommand, npmArguments, childEnvironment);

let isShuttingDown = false;

function shutdown(exitCode = 0) {
  if (isShuttingDown) {
    return;
  }
  isShuttingDown = true;
  terminateProcess(apiProcess);
  terminateProcess(webProcess);
  setTimeout(() => process.exit(exitCode), 500);
}

function terminateProcess(child) {
  if (!child.pid) {
    return;
  }

  if (process.platform === "win32") {
    spawn("taskkill", ["/pid", String(child.pid), "/t", "/f"], {
      stdio: "ignore",
      windowsHide: true,
    });
    return;
  }

  child.kill("SIGTERM");
}

process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));

apiProcess.on("exit", (code) => {
  if (!isShuttingDown) {
    console.error(`Backend exited with code ${code ?? "unknown"}.`);
    shutdown(code ?? 1);
  }
});

webProcess.on("exit", (code) => {
  if (!isShuttingDown) {
    console.error(`Frontend exited with code ${code ?? "unknown"}.`);
    shutdown(code ?? 1);
  }
});
