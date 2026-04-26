/**
 * Performance Monitoring Utility
 * Provides tools to monitor Three.js rendering performance
 * 
 * Validates: Requirement 18.3 - Verify draw call reduction (target: <50 per frame)
 */

/**
 * Get rendering statistics from Three.js renderer
 * 
 * @param {THREE.WebGLRenderer} renderer - The Three.js renderer instance
 * @returns {Object} Rendering statistics including draw calls, triangles, and points
 */
export function getRenderStats(renderer) {
  if (!renderer || !renderer.info) {
    return null;
  }

  const info = renderer.info;
  
  return {
    drawCalls: info.render.calls,
    triangles: info.render.triangles,
    points: info.render.points,
    lines: info.render.lines,
    frame: info.render.frame,
    memory: {
      geometries: info.memory.geometries,
      textures: info.memory.textures,
    },
  };
}

/**
 * Log rendering statistics to console
 * Useful for debugging and performance verification
 * 
 * @param {THREE.WebGLRenderer} renderer - The Three.js renderer instance
 */
export function logRenderStats(renderer) {
  const stats = getRenderStats(renderer);
  
  if (!stats) {
    console.warn('Performance Monitor: Renderer not available');
    return;
  }

  console.group('🎨 Render Performance Stats');
  console.log(`Draw Calls: ${stats.drawCalls} ${stats.drawCalls < 50 ? '✅' : '⚠️'} (target: <50)`);
  console.log(`Triangles: ${stats.triangles.toLocaleString()}`);
  console.log(`Points: ${stats.points.toLocaleString()}`);
  console.log(`Frame: ${stats.frame}`);
  console.log(`Geometries in Memory: ${stats.memory.geometries}`);
  console.log(`Textures in Memory: ${stats.memory.textures}`);
  console.groupEnd();
}

/**
 * Create a performance monitor that logs stats periodically
 * 
 * @param {THREE.WebGLRenderer} renderer - The Three.js renderer instance
 * @param {number} intervalMs - Interval in milliseconds between logs (default: 5000)
 * @returns {Function} Cleanup function to stop monitoring
 */
export function createPerformanceMonitor(renderer, intervalMs = 5000) {
  const intervalId = setInterval(() => {
    logRenderStats(renderer);
  }, intervalMs);

  // Return cleanup function
  return () => clearInterval(intervalId);
}
