/**
 * Reference Gaia-X metadata router for Express.
 *
 * Mount this in your existing app:
 *
 *   const gaiaxRouter = require('./api/express_example');
 *   app.use('/gaia-x', gaiaxRouter);
 *
 * Serves the static credentials generated into .well-known/, plus one
 * example of merging a static policy claim with a live value from your own
 * database — copy this pattern for any policy field your app already
 * tracks dynamically, rather than letting a static file drift out of sync.
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
router.get('/service-offering', handle('service-offering.json'));
router.get('/terms-and-conditions', handle('tnc.json'));
router.get('/compliance-credential', handle('compliance-credential.json'));

router.get('/policy', (req, res, next) => {
  try {
    const staticPolicy = load('policy.json');
    // Replace with a real query against whatever in your app enforces
    // retention/sharing/deletion — don't leave this hardcoded.
    staticPolicy.liveRetentionRules = getLiveRetentionRules();
    res.json(staticPolicy);
  } catch (err) {
    next(err);
  }
});

function getLiveRetentionRules() {
  // Stub — replace with a real DB query, e.g.:
  // return db.cleanupPolicies.findMany().map(p => ({ name: p.name, maxAgeDays: p.maxAgeDays }));
  return [];
}

module.exports = router;
