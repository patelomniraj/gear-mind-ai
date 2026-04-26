import * as THREE from 'three';

/**
 * ============================================================
 *  INVOLUTE GEAR GEOMETRY UTILITIES
 * ============================================================
 *
 * All gears use a true involute tooth profile, which is the
 * industry-standard tooth shape for smooth meshing.
 *
 * Key formulas:
 *  pitchR  = module * teeth / 2
 *  baseR   = pitchR * cos(20°)           // pressure angle 20°
 *  tipR    = pitchR + module              // addendum = 1 module
 *  rootR   = pitchR - 1.25 * module      // dedendum = 1.25 modules
 *
 * Involute curve (parameterised by t):
 *  x(t) = baseR * (cos(t) + t * sin(t))
 *  y(t) = baseR * (sin(t) - t * cos(t))
 *
 * Centering offset per tooth:
 *  halfTooth = π / (2 * numTeeth)        // circular pitch / 2 → radians
 *  invAlpha  = tan(φ) − φ               // involute function at pressure angle
 *  offset    = halfTooth + invAlpha
 * ============================================================
 */

const PRESSURE_ANGLE = (20 * Math.PI) / 180;

/** Parametric involute point relative to baseR at roll angle t. */
function invPt(baseR, t) {
  return {
    x: baseR * (Math.cos(t) + t * Math.sin(t)),
    y: baseR * (Math.sin(t) - t * Math.cos(t)),
  };
}

/**
 * Builds a THREE.Shape representing the 2D cross-section of an involute gear.
 *
 * @param {number} module      - Gear module (controls tooth size)
 * @param {number} numTeeth    - Number of teeth
 * @param {number} holeRadius  - Bore hole radius (0 = no hole)
 * @param {boolean} addSpokes  - Punch lightening holes between hub and rim
 */
export function buildGearShape(module, numTeeth, holeRadius = 0, addSpokes = false) {
  const m = module;
  const z = numTeeth;

  const pitchR = (m * z) / 2;
  const baseR  = pitchR * Math.cos(PRESSURE_ANGLE);
  const tipR   = pitchR + m;
  // Ensure root never dips below the base circle (would cause undercut artefacts)
  const rootR  = Math.max(pitchR - 1.25 * m, baseR * 1.002);

  const toothAngle = (2 * Math.PI) / z;
  const halfTooth  = Math.PI / (2 * z);                // half angular tooth thickness at pitch circle
  const invAlpha   = Math.tan(PRESSURE_ANGLE) - PRESSURE_ANGLE;
  const offset     = halfTooth + invAlpha;

  // t-parameter at root and tip circles
  const tRoot = Math.sqrt(Math.max(0, (rootR / baseR) ** 2 - 1));
  const tTip  = Math.sqrt(Math.max(0, (tipR  / baseR) ** 2 - 1));

  const pRoot = invPt(baseR, tRoot);
  const pTip  = invPt(baseR, tTip);
  const thetaRoot = Math.atan2(pRoot.y, pRoot.x);
  const thetaTip  = Math.atan2(pTip.y,  pTip.x);

  const shape = new THREE.Shape();
  let first = true;

  const addPt = (x, y) => {
    if (first) { shape.moveTo(x, y); first = false; }
    else shape.lineTo(x, y);
  };

  const ROOT_STEPS = 5;
  const INV_STEPS  = 12;  // more steps → smoother involute flank
  const TIP_STEPS  = 4;

  for (let i = 0; i < z; i++) {
    const baseA = i * toothAngle;

    /* ── Root arc (tooth space between teeth) ─────────────────────────── */
    const rootArcFrom = baseA - toothAngle / 2 + 0.02;           // tiny offset avoids crease
    const rootArcTo   = baseA - offset + thetaRoot;
    for (let j = 0; j <= ROOT_STEPS; j++) {
      const a = rootArcFrom + (rootArcTo - rootArcFrom) * (j / ROOT_STEPS);
      addPt(rootR * Math.cos(a), rootR * Math.sin(a));
    }

    /* ── Right flank (involute from root → tip) ───────────────────────── */
    for (let j = 0; j <= INV_STEPS; j++) {
      const t = tRoot + (tTip - tRoot) * (j / INV_STEPS);
      const p = invPt(baseR, t);
      const r = Math.hypot(p.x, p.y);
      const a = Math.atan2(p.y, p.x) - offset + baseA;
      addPt(r * Math.cos(a), r * Math.sin(a));
    }

    /* ── Tip arc (short arc across the tooth crown) ───────────────────── */
    const tipRight = thetaTip - offset + baseA;
    const tipLeft  = -(thetaTip - offset) + baseA;
    for (let j = 0; j <= TIP_STEPS; j++) {
      const a = tipRight + (tipLeft - tipRight) * (j / TIP_STEPS);
      addPt(tipR * Math.cos(a), tipR * Math.sin(a));
    }

    /* ── Left flank (mirrored involute from tip → root) ──────────────── */
    for (let j = INV_STEPS; j >= 0; j--) {
      const t = tRoot + (tTip - tRoot) * (j / INV_STEPS);
      const p = invPt(baseR, t);
      const r = Math.hypot(p.x, p.y);
      const a = -(Math.atan2(p.y, p.x) - offset) + baseA;
      addPt(r * Math.cos(a), r * Math.sin(a));
    }
  }

  shape.closePath();

  /* ── Bore hole ───────────────────────────────────────────────────────── */
  if (holeRadius > 0) {
    const hole = new THREE.Path();
    hole.absarc(0, 0, holeRadius, 0, Math.PI * 2, true);
    shape.holes.push(hole);
  }

  /* ── Spoke lightening holes ──────────────────────────────────────────── */
  if (addSpokes && holeRadius > 0) {
    const ns      = 5;
    const spokeR  = (rootR * 0.55 + holeRadius * 1.9) / 2;
    const holeR   = Math.min((rootR - holeRadius) * 0.21, spokeR - holeRadius - 0.06);
    if (holeR > 0.04) {
      for (let i = 0; i < ns; i++) {
        const a    = (i / ns) * Math.PI * 2 + toothAngle * 0.5;
        const hole = new THREE.Path();
        hole.absarc(spokeR * Math.cos(a), spokeR * Math.sin(a), holeR, 0, Math.PI * 2, true);
        shape.holes.push(hole);
      }
    }
  }

  return shape;
}

/* ─────────────────────────────────────────────────────────────────────────────
 *  PUBLIC GEOMETRY FACTORIES
 * ───────────────────────────────────────────────────────────────────────────── */

/**
 * Spur gear — straight teeth, bevel chamfer on faces.
 *
 * module=0.25, teeth=36 → pitch diameter ≈ 9 units
 */
export function createSpurGearGeometry(
  module     = 0.25,
  numTeeth   = 36,
  faceWidth  = 0.60,
  holeRadius = 0.55,
) {
  const shape = buildGearShape(module, numTeeth, holeRadius, true);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth:          faceWidth,
    bevelEnabled:   true,
    bevelThickness: module * 0.14,
    bevelSize:      module * 0.11,
    bevelSegments:  3,
    curveSegments:  14,          // smooth curves on involute flanks
  });

  geo.center();
  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

/**
 * Helical gear — same involute cross-section as spur, but vertices are
 * progressively rotated along the extrusion axis to simulate helix twist.
 *
 * helixAngle > 0 → right-hand helix,  < 0 → left-hand helix
 */
export function createHelicalGearGeometry(
  module     = 0.28,
  numTeeth   = 28,
  faceWidth  = 0.80,
  helixAngle = 20,
  holeRadius = 0.40,
) {
  const shape   = buildGearShape(module, numTeeth, holeRadius, false);
  const pitchR  = (module * numTeeth) / 2;
  // Total angular twist across the face width
  const totalTwist = Math.tan((helixAngle * Math.PI) / 180) * faceWidth / pitchR;

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth:          faceWidth,
    bevelEnabled:   true,
    bevelThickness: module * 0.10,
    bevelSize:      module * 0.08,
    bevelSegments:  3,
    curveSegments:  14,
  });

  geo.center();

  // Apply progressive rotation (twist) to every vertex based on its Z position.
  // After center(), Z ranges approximately −faceWidth/2 → +faceWidth/2.
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const z    = pos.getZ(i);
    const t    = (z + faceWidth / 2) / faceWidth;  // 0 → 1 along face
    const ang  = t * totalTwist;
    const cos  = Math.cos(ang);
    const sin  = Math.sin(ang);
    const x    = pos.getX(i);
    const y    = pos.getY(i);
    pos.setX(i, x * cos - y * sin);
    pos.setY(i, x * sin + y * cos);
  }
  pos.needsUpdate = true;

  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

/**
 * Bevel gear — involute cross-section extruded then tapered toward one face
 * to create the conical frustum profile of a true bevel gear.
 */
export function createBevelGearGeometry(
  module     = 0.35,
  numTeeth   = 20,
  faceWidth  = 1.10,
  holeRadius = 0.42,
  taper      = 0.38,    // scale factor reduction at narrow face (0 = cylinder, 0.5 = half)
) {
  const shape = buildGearShape(module, numTeeth, holeRadius, false);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth:          faceWidth,
    bevelEnabled:   true,
    bevelThickness: module * 0.10,
    bevelSize:      module * 0.08,
    bevelSegments:  3,
    curveSegments:  14,
  });

  geo.center();

  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const z      = pos.getZ(i);
    const t      = (z + faceWidth / 2) / faceWidth;       // 0 → 1
    const scale  = 1 - taper * t;
    pos.setX(i, pos.getX(i) * scale);
    pos.setY(i, pos.getY(i) * scale);
  }
  pos.needsUpdate = true;

  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

/**
 * Worm gear wheel — same as a spur gear, used as the driven wheel in a worm assembly.
 */
export function createWormWheelGeometry(
  module     = 0.30,
  numTeeth   = 20,
  faceWidth  = 1.10,
  holeRadius = 0.48,
) {
  const shape = buildGearShape(module, numTeeth, holeRadius, false);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth:          faceWidth,
    bevelEnabled:   true,
    bevelThickness: module * 0.10,
    bevelSize:      module * 0.08,
    bevelSegments:  3,
    curveSegments:  14,
  });

  geo.center();
  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

/**
 * Worm spiral geometry — a cylinder with a helical Acme-profile thread ridge.
 * Built from scratch as a BufferGeometry by sweeping a trapezoidal cross-section
 * along a helix path.
 */
export function createWormSpiral(
  shaftRadius  = 0.40,
  length       = 4.0,
  pitch        = 0.55,
  threadHeight = 0.22,
) {
  const turns      = length / pitch;
  const SEG_TURN   = 40;           // segments per full revolution
  const totalSeg   = Math.ceil(turns * SEG_TURN);
  const PROF       = 10;           // profile points per cross-section (trapezoidal ridge)

  const verts  = [];
  const idxs   = [];

  for (let i = 0; i <= totalSeg; i++) {
    const t     = i / totalSeg;
    const angle = t * turns * Math.PI * 2;
    const zBase = t * length - length / 2;

    for (let j = 0; j <= PROF; j++) {
      const pa = (j / PROF) * Math.PI;          // 0 → π (half-circle profile)
      // Smooth Acme thread profile using a raised cosine ridge
      const ridge = threadHeight * 0.5 * (1 - Math.cos(pa));
      const r     = shaftRadius + ridge;
      // Slight axial shift creates the lead angle on the ridge flanks
      const dz    = (j / PROF - 0.5) * pitch * 0.55;

      verts.push(r * Math.cos(angle), r * Math.sin(angle), zBase + dz);
    }
  }

  for (let i = 0; i < totalSeg; i++) {
    for (let j = 0; j < PROF; j++) {
      const a = i       * (PROF + 1) + j;
      const b = (i + 1) * (PROF + 1) + j;
      idxs.push(a, b, a + 1);
      idxs.push(b, b + 1, a + 1);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geo.setIndex(idxs);

  // Add UV attribute so mergeGeometries doesn't fail:
  // CylinderGeometry has position+normal+uv; all merged geometries must share the same set.
  const uvs = new Float32Array((verts.length / 3) * 2); // zero-filled UVs
  geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));

  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

/* ─────────────────────────────────────────────────────────────────────────────
 *  LEGACY COMPATIBILITY EXPORTS
 *  (keep old function signatures intact so existing callers don't break)
 * ───────────────────────────────────────────────────────────────────────────── */

export function createSpurTeeth(pitchRadius, numTeeth, _toothHeight, _toothWidth, faceWidth) {
  const m = (pitchRadius * 2) / numTeeth;
  return createSpurGearGeometry(m, numTeeth, faceWidth, pitchRadius * 0.28);
}

export function createHelicalTooth(helixAngle, faceWidth) {
  // Legacy shim — returns a single tooth shape; callers now use createHelicalGearGeometry.
  const shape = new THREE.Shape();
  const w = 0.22, h = 0.42;
  shape.moveTo(-w, 0);
  shape.quadraticCurveTo(-w * 0.6, h * 0.4, -w * 0.25, h);
  shape.lineTo(w * 0.25, h);
  shape.quadraticCurveTo(w * 0.6, h * 0.4, w, 0);
  shape.closePath();
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: faceWidth, bevelEnabled: true,
    bevelThickness: 0.025, bevelSize: 0.02, bevelSegments: 2, curveSegments: 6,
  });
  return geo;
}