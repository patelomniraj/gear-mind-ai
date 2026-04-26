import * as THREE from 'three';

/**
 * Shared MeshPhysicalMaterial for all gear components.
 *
 * Key upgrades over MeshStandardMaterial:
 *  - clearcoat: simulates the thin polished coating of precision-machined steel
 *  - high metalness + low roughness: cold-rolled steel appearance
 *  - envMapIntensity: strong reflections when an HDRI environment map is present
 *
 * Shared instance eliminates redundant GPU state changes between draw calls.
 */

let _sharedMaterial = null;

export function getSharedGearMaterial() {
  if (!_sharedMaterial) {
    _sharedMaterial = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(0x4e5d6e),   // Cold-rolled steel: blue-gray cast
      metalness: 0.92,
      roughness: 0.22,                     // Slightly increased for better tooth definition
      clearcoat: 0.50,                     // Increased clearcoat for sharper edges
      clearcoatRoughness: 0.08,            // Smoother clearcoat for better definition
      envMapIntensity: 2.2,                // Strong env-map reflections (needs <Environment>)
      side: THREE.FrontSide,
      flatShading: false,                  // Smooth shading for better tooth visibility
    });
  }
  return _sharedMaterial;
}

/**
 * Darker variant for bore holes / recessed surfaces.
 * Called per-component so callers must dispose() it themselves.
 */
export function createBoreMaterial() {
  return new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0x252c35),
    metalness: 0.85,
    roughness: 0.45,
    clearcoat: 0.1,
    clearcoatRoughness: 0.4,
  });
}

export function disposeSharedMaterial() {
  if (_sharedMaterial) {
    _sharedMaterial.dispose();
    _sharedMaterial = null;
  }
}