/**
 * Hero — 3D extruded Sphera Films logo (Three.js)
 */
import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";
import { SVGLoader } from "https://unpkg.com/three@0.160.0/examples/jsm/loaders/SVGLoader.js";

const LOGO_URL = "assets/logo-white.svg";
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function initHero3D(canvas) {
  if (!canvas) return () => {};

  const renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
    powerPreference: "high-performance",
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 200);
  camera.position.set(0, 0, 14);

  const ambient = new THREE.AmbientLight(0xffffff, 0.35);
  const key = new THREE.DirectionalLight(0xffffff, 1.2);
  key.position.set(4, 6, 8);
  const rim = new THREE.DirectionalLight(0x8ec8ff, 0.9);
  rim.position.set(-6, -2, 4);
  const fill = new THREE.PointLight(0x8899cc, 0.5, 40);
  fill.position.set(0, -4, 6);
  scene.add(ambient, key, rim, fill);

  const group = new THREE.Group();
  scene.add(group);

  const loader = new SVGLoader();
  let mesh = null;
  let disposed = false;

  loader.load(
    LOGO_URL,
    (data) => {
      if (disposed) return;
      const shapes = [];
      for (const path of data.paths) {
        shapes.push(...SVGLoader.createShapes(path));
      }
      if (!shapes.length) return;

      const opts = {
        depth: 28,
        bevelEnabled: true,
        bevelThickness: 3,
        bevelSize: 2,
        bevelSegments: 3,
        curveSegments: 12,
      };

      const mat = new THREE.MeshStandardMaterial({
        color: 0xf4f2ee,
        metalness: 0.72,
        roughness: 0.28,
      });

      const logoGroup = new THREE.Group();
      for (const shape of shapes) {
        const geo = new THREE.ExtrudeGeometry(shape, opts);
        logoGroup.add(new THREE.Mesh(geo, mat));
      }

      logoGroup.rotation.x = Math.PI;
      const box = new THREE.Box3().setFromObject(logoGroup);
      const size = new THREE.Vector3();
      box.getSize(size);
      const center = new THREE.Vector3();
      box.getCenter(center);
      logoGroup.position.sub(center);
      const scale = 5.8 / Math.max(size.x, size.y, 0.001);
      logoGroup.scale.setScalar(scale);
      logoGroup.scale.z *= 0.55;

      mesh = logoGroup;
      group.add(mesh);
    },
    undefined,
    (err) => console.warn("Hero 3D logo load failed", err)
  );

  const resize = () => {
    const parent = canvas.parentElement;
    if (!parent) return;
    const w = parent.clientWidth;
    const h = parent.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  };

  resize();
  const ro = new ResizeObserver(resize);
  ro.observe(canvas.parentElement);

  let t0 = performance.now();
  let raf = 0;

  const tick = (now) => {
    if (disposed) return;
    raf = requestAnimationFrame(tick);
    const t = (now - t0) * 0.001;
    if (!REDUCED) {
      group.rotation.y = t * 0.35;
      group.rotation.x = Math.sin(t * 0.4) * 0.12 - 0.08;
      group.position.y = Math.sin(t * 0.55) * 0.15;
    }
    renderer.render(scene, camera);
  };
  tick(t0);

  return () => {
    disposed = true;
    cancelAnimationFrame(raf);
    ro.disconnect();
    mesh?.traverse((obj) => {
      if (obj.isMesh) {
        obj.geometry?.dispose();
        obj.material?.dispose();
      }
    });
    renderer.dispose();
  };
}
