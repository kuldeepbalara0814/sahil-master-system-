import { Router } from "express";
import { execFile } from "child_process";
import path from "path";
import { promisify } from "util";

const execFileAsync = promisify(execFile);
const router = Router();

const PYTHON = "python3";
const API_SCRIPT = path.resolve(
  path.dirname(new URL(import.meta.url).pathname),
  "../../..",
  "sahil_system/api.py"
);

async function callPython(command: string, args: Record<string, unknown> = {}): Promise<unknown> {
  const { stdout } = await execFileAsync(PYTHON, [API_SCRIPT, command, JSON.stringify(args)], {
    cwd: path.dirname(API_SCRIPT),
    timeout: 30000,
  });
  return JSON.parse(stdout.trim());
}

// GET /api/sahil/records
router.get("/records", async (req, res) => {
  try {
    const data = await callPython("records_list");
    res.json(data);
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Records load nahi hue" });
  }
});

// POST /api/sahil/records
router.post("/records", async (req, res) => {
  try {
    const result = await callPython("records_add", req.body) as Record<string, unknown>;
    if (result.conflict) {
      res.status(409).json({ error: result.message });
    } else if (!result.success) {
      res.status(400).json({ error: result.message });
    } else {
      res.status(201).json({ success: true, message: result.message as string });
    }
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Record save nahi hua" });
  }
});

// PUT /api/sahil/records/:date
router.put("/records/:date", async (req, res) => {
  try {
    const result = await callPython("records_update", { ...req.body, date: req.params.date }) as Record<string, unknown>;
    if (result.notFound) {
      res.status(404).json({ error: result.message });
    } else {
      res.json({ success: true, message: result.message as string });
    }
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Record update nahi hua" });
  }
});

// GET /api/sahil/pending
router.get("/pending", async (req, res) => {
  try {
    const data = await callPython("pending_get");
    res.json(data);
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Pending load nahi hua" });
  }
});

// POST /api/sahil/pending
router.post("/pending", async (req, res) => {
  try {
    const data = await callPython("pending_save", req.body);
    res.json(data);
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Pending save nahi hua" });
  }
});

// POST /api/sahil/predict
router.post("/predict", async (req, res) => {
  try {
    const data = await callPython("predict", req.body);
    res.json(data);
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Prediction run nahi hui" });
  }
});

// GET /api/sahil/predictions
router.get("/predictions", async (req, res) => {
  try {
    const data = await callPython("predictions_list");
    res.json(data);
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Predictions load nahi hui" });
  }
});

// POST /api/sahil/predictions/check
router.post("/predictions/check", async (req, res) => {
  try {
    const data = await callPython("predictions_check", req.body);
    res.json(data);
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Check nahi hua" });
  }
});

// GET /api/sahil/stats
router.get("/stats", async (req, res) => {
  try {
    const data = await callPython("stats");
    res.json(data);
  } catch (e) {
    req.log.error(e);
    res.status(500).json({ error: "Stats load nahi hui" });
  }
});

export default router;
