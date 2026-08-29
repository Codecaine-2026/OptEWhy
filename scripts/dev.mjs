import { existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, delimiter, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn, spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { initdb, pg_ctl, postgres } from "@embedded-postgres/windows-x64";

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

function configureLocalDatabase(environment) {
  const databaseUrl = environment.DATABASE_URL?.trim();
  if (!databaseUrl) {
    console.error("DATABASE_URL is required to run the local API with PostgreSQL.");
    process.exit(1);
  }

  try {
    const parsedUrl = new URL(databaseUrl);
    if (parsedUrl.hostname === "postgres") {
      parsedUrl.hostname = "127.0.0.1";
      environment.DATABASE_URL = parsedUrl.toString();
    }
  } catch {
    console.error("DATABASE_URL must be a valid PostgreSQL connection URL.");
    process.exit(1);
  }
}

let postgresProcess;

function runPostgresCommand(command, args) {
  return new Promise((resolve, reject) => {
    const process = spawn(command, args, { cwd: repoRoot, stdio: "inherit" });
    process.once("error", reject);
    process.once("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`PostgreSQL command failed with exit code ${code ?? "unknown"}.`));
      }
    });
  });
}

async function startEmbeddedPostgres(environment) {
  const parsedUrl = new URL(environment.DATABASE_URL);
  const port = Number(parsedUrl.port || 5432);
  const databaseDir = join("postgres-data", "embedded");
  const user = decodeURIComponent(parsedUrl.username) || "optewhy";
  const passwordPath = join(tmpdir(), `optewhy-pg-password-${process.pid}`);

  if (!existsSync(join(databaseDir, "PG_VERSION"))) {
    console.log("Initializing project-local PostgreSQL data...");
    writeFileSync(passwordPath, `${decodeURIComponent(parsedUrl.password) || "optewhy"}\n`);
    try {
      await runPostgresCommand(initdb, [
        `--pgdata=${databaseDir}`,
        "--auth=password",
        `--username=${user}`,
        `--pwfile=${passwordPath}`,
        "--locale=C",
        "--encoding=UTF8",
      ]);
    } finally {
      rmSync(passwordPath, { force: true });
    }
  }

  console.log("Starting project-local PostgreSQL service...");
  postgresProcess = spawn(postgres, ["-D", databaseDir, "-p", String(port)], {
    cwd: repoRoot,
    stdio: ["ignore", "ignore", "pipe"],
  });

  await new Promise((resolve, reject) => {
    postgresProcess.once("error", reject);
    postgresProcess.once("close", () => reject(new Error("PostgreSQL stopped before becoming ready.")));
    postgresProcess.stderr.on("data", (chunk) => {
      const message = chunk.toString("utf8");
      process.stderr.write(message);
      if (message.includes("database system is ready to accept connections")) {
        resolve();
      }
    });
  });
}

async function stopEmbeddedPostgres() {
  if (!postgresProcess) {
    return;
  }

  await runPostgresCommand(pg_ctl, ["-D", join("postgres-data", "embedded"), "stop", "-m", "fast", "-w"]);
  postgresProcess = undefined;
}

function initializeApplicationDatabase(environment, pythonCommand) {
  const result = spawnSync(
    pythonCommand,
    [join(repoRoot, "scripts", "seed-demo-data", "initialize_local_database.py")],
    {
      cwd: repoRoot,
      env: environment,
      stdio: "inherit",
      windowsHide: false,
    },
  );

  if (result.error || result.status !== 0) {
    console.error("Unable to initialize the project-local PostgreSQL database.");
    process.exit(1);
  }
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
configureLocalDatabase(childEnvironment);
appendPythonPath(childEnvironment);

const localPythonCommand =
  process.platform === "win32"
    ? join(repoRoot, ".venv", "Scripts", "python.exe")
    : join(repoRoot, ".venv", "bin", "python");
const fallbackPythonCommand = process.platform === "win32" ? "python" : "python3";
const pythonCommand = process.env.PYTHON ??
  (existsSync(localPythonCommand) ? localPythonCommand : fallbackPythonCommand);
await startEmbeddedPostgres(childEnvironment);
initializeApplicationDatabase(childEnvironment, pythonCommand);
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

async function shutdown(exitCode = 0) {
  if (isShuttingDown) {
    return;
  }
  isShuttingDown = true;
  await Promise.all([terminateProcess(apiProcess), terminateProcess(webProcess)]);
  try {
    await stopEmbeddedPostgres();
  } catch (error) {
    console.error("Unable to stop project-local PostgreSQL cleanly.", error);
  }
  process.exit(exitCode);
}

function terminateProcess(child) {
  return new Promise((resolve) => {
    if (!child.pid || child.exitCode !== null) {
      resolve();
      return;
    }

    if (process.platform === "win32") {
      const terminator = spawn("taskkill", ["/pid", String(child.pid), "/t", "/f"], {
        stdio: "ignore",
        windowsHide: true,
      });
      terminator.once("error", resolve);
      terminator.once("close", resolve);
      return;
    }

    child.once("exit", resolve);
    child.kill("SIGTERM");
  });
}

process.on("SIGINT", () => void shutdown(0));
process.on("SIGTERM", () => void shutdown(0));

apiProcess.on("exit", (code) => {
  if (!isShuttingDown) {
    console.error(`Backend exited with code ${code ?? "unknown"}.`);
    void shutdown(code ?? 1);
  }
});

webProcess.on("exit", (code) => {
  if (!isShuttingDown) {
    console.error(`Frontend exited with code ${code ?? "unknown"}.`);
    void shutdown(code ?? 1);
  }
});
