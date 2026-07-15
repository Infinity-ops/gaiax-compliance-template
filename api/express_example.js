/**
 * Reference Gaia-X metadata router for Express.
 *
 * Mount this in your existing app:
 *
 *   const gaiaxRouter = require('./api/express_example');
 *   app.use('/gaia-x', gaiaxRouter);
 */
const express = require('express');
const fs = require('fs');
const path = require('path');

const router = express.Router();
const WELL_KNOWN_DIR = path.join(__dirname, '..', '.well-known');

function load(filename) {
  const filePath = path.join(WELL_KNOWN_DIR, filename);
  if (!fs.existsSync(filePath)) {
    const err = new Error(`${filename} not generated yet — run scripts/build_credentials.py`);
    err.status = 503;
    throw err;
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function listIds(prefix, suffix = '.json') {
  return fs.readdirSync(WELL_KNOWN_DIR)
    .filter((f) => f.startsWith(prefix) && f.endsWith(suffix))
    .map((f) => f.slice(prefix.length, -suffix.length));
}

function handle(filename) {
  return (req, res, next) => {
    try {
      res.json(load(filename));
    } catch (err) {
      next(err);
    }
  };
}

router.get('/participant', handle('participant.json'));
router.get('/terms-and-conditions', handle('tnc.json'));
router.get('/compliance-credential', handle('compliance-credential.json'));

router.get('/service-offerings', (req, res) => {
  res.json({ offerings: listIds('service-offering-') });
});
router.get('/service-offerings/:id', (req, res, next) => {
  try {
    res.json(load(`service-offering-${req.params.id}.json`));
  } catch (err) {
    next(err);
  }
});

router.get('/data-resources', (req, res) => {
  res.json({ resources: listIds('data-resource-') });
});
router.get('/data-resources/:id', (req, res, next) => {
  try {
    res.json(load(`data-resource-${req.params.id}.json`));
  } catch (err) {
    next(err);
  }
});

router.get('/policy', (req, res, next) => {
  try {
    const staticPolicy = load('policy.json');
    // Replace with a real query against whatever in your app enforces
    // retention/sharing/deletion — don't leave this hardcoded.
    const liveFacts = {};
    if (Object.keys(liveFacts).length) staticPolicy.liveFacts = liveFacts;
    res.json(staticPolicy);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
