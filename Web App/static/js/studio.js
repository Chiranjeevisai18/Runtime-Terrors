/**
 * Gruha Alankara – Three.js 3D Visualization Studio
 * Fixed: camera inside room, DoubleSide walls, AI recommendation fallback, furniture list self-contained.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// ============================================================
// Global State
// ============================================================
let scene, camera, renderer, controls;
let raycaster, mouse;
let roomBox = null;
let gridHelper = null;
let selectedObject = null;
let isDragging = false;
let dragPlane;
let dragOffset = new THREE.Vector3();
let furnitureObjects = [];
let showGrid = true;
let showRoomWalls = true;
let gltfLoader = null;

const studioData = window.STUDIO_DATA || {
    designId: 0, faceUrls: {}, imagePath: '',
    roomType: 'living_room', style: 'modern',
    aiOutput: {}, placements: [], csrfToken: ''
};

// ============================================================
// Name Aliases — maps AI-returned names to GEO keys
// ============================================================
const NAME_ALIASES = {
    // sofa variations
    couch: 'sofa', settee: 'sofa', loveseat: 'sofa', sectional: 'sofa',
    sectional_sofa: 'sofa', three_seater: 'sofa', two_seater: 'sofa',
    l_shaped_sofa: 'sofa', modular_sofa: 'sofa', sleeper_sofa: 'sofa',

    // table variations
    coffee_table: 'table', center_table: 'table', occasional_table: 'table',
    cocktail_table: 'table', end_table: 'table', accent_table: 'table',
    console_table: 'table', tea_table: 'table',

    // chair variations
    armchair: 'chair', arm_chair: 'chair', accent_chair: 'chair',
    lounge_chair: 'chair', dining_chair: 'chair', office_chair: 'chair',
    recliner: 'chair', rocking_chair: 'chair', stool: 'chair',
    bar_stool: 'chair', ottoman: 'chair', pouf: 'chair', bench: 'chair',

    // bed variations
    queen_bed: 'bed', king_bed: 'bed', double_bed: 'bed',
    single_bed: 'bed', twin_bed: 'bed', platform_bed: 'bed',
    bed_frame: 'bed', cot: 'bed', mattress: 'bed', bunk_bed: 'bed',

    // wardrobe variations
    closet: 'wardrobe', cupboard: 'wardrobe', armoire: 'wardrobe',
    cabinet: 'wardrobe', storage_cabinet: 'wardrobe', dresser: 'wardrobe',
    chest_of_drawers: 'wardrobe', tallboy: 'wardrobe',

    // bookshelf variations
    bookcase: 'bookshelf', book_shelf: 'bookshelf', shelving_unit: 'bookshelf',
    shelf: 'bookshelf', shelves: 'bookshelf', storage_shelf: 'bookshelf',
    display_shelf: 'bookshelf', wall_shelf: 'bookshelf', rack: 'bookshelf',
    display_unit: 'bookshelf', floating_shelf: 'bookshelf',

    // lamp variations
    floor_lamp: 'lamp', table_lamp: 'lamp', desk_lamp: 'lamp',
    pendant_light: 'lamp', chandelier: 'lamp', light: 'lamp',
    lighting: 'lamp', standing_lamp: 'lamp', reading_lamp: 'lamp',
    wall_sconce: 'lamp', sconce: 'lamp', ceiling_light: 'lamp',

    // desk variations
    study_desk: 'desk', work_desk: 'desk', writing_desk: 'desk',
    computer_desk: 'desk', study_table: 'desk', work_table: 'desk',
    workstation: 'desk', office_desk: 'desk', vanity: 'desk',

    // rug variations
    carpet: 'rug', area_rug: 'rug', floor_mat: 'rug', mat: 'rug',
    runner: 'rug', floor_covering: 'rug',

    // tv_stand variations
    tv_unit: 'tv_stand', tv_cabinet: 'tv_stand', entertainment_center: 'tv_stand',
    media_console: 'tv_stand', entertainment_unit: 'tv_stand',
    media_unit: 'tv_stand', tv_table: 'tv_stand', television_stand: 'tv_stand',
    television_unit: 'tv_stand',

    // dining_table variations
    dining_set: 'dining_table', dinner_table: 'dining_table',
    kitchen_table: 'dining_table', eating_table: 'dining_table',

    // side_table variations
    nightstand: 'side_table', night_stand: 'side_table',
    bedside_table: 'side_table', end_table_small: 'side_table',
    accent_table_small: 'side_table', pedestal_table: 'side_table',

    // plant variations
    indoor_plant: 'plant', houseplant: 'plant', potted_plant: 'plant',
    flower_pot: 'plant', planter: 'plant', succulent: 'plant',
    greenery: 'plant', fern: 'plant', palm: 'plant', cactus: 'plant',
    flower_vase: 'plant', vase: 'plant',

    // mirror variations
    wall_mirror: 'mirror', full_length_mirror: 'mirror',
    dresser_mirror: 'mirror', standing_mirror: 'mirror',
    vanity_mirror: 'mirror', floor_mirror: 'mirror',
};

/**
 * Resolve an AI-returned type string to its canonical GEO key.
 * - Lowercases
 * - Replaces spaces/hyphens with underscores
 * - Strips trailing 's' for plurals
 * - Checks GEO first, then NAME_ALIASES
 */
function resolveType(raw) {
    if (!raw) return raw;
    let t = raw.toLowerCase().replace(/[\s-]+/g, '_').replace(/[^a-z0-9_]/g, '');
    if (GEO[t]) return t;
    if (NAME_ALIASES[t]) return NAME_ALIASES[t];
    // Try without trailing 's' (plural)
    const singular = t.replace(/_?s$/, '');
    if (GEO[singular]) return singular;
    if (NAME_ALIASES[singular]) return NAME_ALIASES[singular];
    // Try each word as a standalone match
    const words = t.split('_');
    for (const w of words) {
        if (GEO[w]) return w;
        if (NAME_ALIASES[w]) return NAME_ALIASES[w];
    }
    console.warn(`[Studio] No match for "${raw}" → "${t}", will use cube fallback`);
    return t;
}

// ============================================================
// Furniture Geometry
// ============================================================
function darkenHex(hex, factor) {
    const c = new THREE.Color(parseInt(String(hex).replace('#', ''), 16));
    c.multiplyScalar(factor);
    return c;
}
function hexInt(hex) { return parseInt(String(hex).replace('#', ''), 16); }

const GEO = {
    sofa(color) {
        const g = new THREE.Group();
        const ci = hexInt(color);
        const seat = new THREE.Mesh(new THREE.BoxGeometry(2, 0.35, 0.9), new THREE.MeshPhongMaterial({ color: ci }));
        seat.position.y = 0.175; g.add(seat);
        const back = new THREE.Mesh(new THREE.BoxGeometry(2, 0.45, 0.15), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.8) }));
        back.position.set(0, 0.525, -0.375); g.add(back);
        [-0.925, 0.925].forEach(x => {
            const arm = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.35, 0.9), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.85) }));
            arm.position.set(x, 0.35, 0); g.add(arm);
        });
        return g;
    },
    table(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        const top = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.05, 0.6), new THREE.MeshPhongMaterial({ color: ci }));
        top.position.y = 0.45; g.add(top);
        [[-0.5, -0.22], [0.5, -0.22], [-0.5, 0.22], [0.5, 0.22]].forEach(([x, z]) => {
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.45, 8), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.7) }));
            leg.position.set(x, 0.225, z); g.add(leg);
        });
        return g;
    },
    chair(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        const seat = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.04, 0.45), new THREE.MeshPhongMaterial({ color: ci }));
        seat.position.y = 0.45; g.add(seat);
        [[-0.18, -0.18], [0.18, -0.18], [-0.18, 0.18], [0.18, 0.18]].forEach(([x, z]) => {
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.45, 6), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.6) }));
            leg.position.set(x, 0.225, z); g.add(leg);
        });
        const back = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.45, 0.04), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.85) }));
        back.position.set(0, 0.695, -0.205); g.add(back);
        return g;
    },
    bed(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        const mat = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.25, 2), new THREE.MeshPhongMaterial({ color: ci }));
        mat.position.y = 0.325; g.add(mat);
        const frame = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.2, 2.1), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.6) }));
        frame.position.y = 0.1; g.add(frame);
        const hb = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.6, 0.08), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.5) }));
        hb.position.set(0, 0.5, -1); g.add(hb);
        const pillow = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.1, 0.3), new THREE.MeshPhongMaterial({ color: 0xf0f0f0 }));
        pillow.position.set(0, 0.5, -0.7); g.add(pillow);
        return g;
    },
    wardrobe(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        const body = new THREE.Mesh(new THREE.BoxGeometry(1.5, 2, 0.6), new THREE.MeshPhongMaterial({ color: ci }));
        body.position.y = 1; g.add(body);
        [-0.08, 0.08].forEach(x => {
            const h = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.12, 8), new THREE.MeshPhongMaterial({ color: 0xcccccc }));
            h.position.set(x, 1, 0.31); g.add(h);
        });
        return g;
    },
    bookshelf(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        [-0.38, 0.38].forEach(x => {
            const s = new THREE.Mesh(new THREE.BoxGeometry(0.04, 1.8, 0.3), new THREE.MeshPhongMaterial({ color: ci }));
            s.position.set(x, 0.9, 0); g.add(s);
        });
        for (let i = 0; i < 5; i++) {
            const sh = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.03, 0.3), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.9) }));
            sh.position.set(0, 0.05 + i * 0.43, 0); g.add(sh);
        }
        return g;
    },
    lamp(color) {
        const g = new THREE.Group();
        g.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.18, 0.05, 16), new THREE.MeshPhongMaterial({ color: 0x333333 })), { position: new THREE.Vector3(0, 0.025, 0) }));
        g.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.2, 8), new THREE.MeshPhongMaterial({ color: 0x666666 })), { position: new THREE.Vector3(0, 0.65, 0) }));
        const shade = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.3, 16, 1, true), new THREE.MeshPhongMaterial({ color: hexInt(color), side: THREE.DoubleSide, emissive: hexInt(color), emissiveIntensity: 0.3 }));
        shade.position.y = 1.35; g.add(shade);
        const glow = new THREE.PointLight(hexInt(color), 0.6, 4); glow.position.y = 1.3; g.add(glow);
        return g;
    },
    desk(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        const top = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.04, 0.6), new THREE.MeshPhongMaterial({ color: ci }));
        top.position.y = 0.75; g.add(top);
        [[-0.55, -0.25], [0.55, -0.25], [-0.55, 0.25], [0.55, 0.25]].forEach(([x, z]) => {
            const leg = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.75, 0.04), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.7) }));
            leg.position.set(x, 0.375, z); g.add(leg);
        });
        return g;
    },
    rug(color) {
        const g = new THREE.Group();
        const r = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.02, 1.5), new THREE.MeshPhongMaterial({ color: hexInt(color), side: THREE.DoubleSide }));
        r.position.y = 0.01; g.add(r);
        return g;
    },
    tv_stand(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        const body = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.5, 0.4), new THREE.MeshPhongMaterial({ color: ci }));
        body.position.y = 0.25; g.add(body);
        const tv = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.7, 0.04), new THREE.MeshPhongMaterial({ color: 0x111111, emissive: 0x111133, emissiveIntensity: 0.3 }));
        tv.position.set(0, 0.85, -0.05); g.add(tv);
        return g;
    },
    dining_table(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        const top = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.05, 0.9), new THREE.MeshPhongMaterial({ color: ci }));
        top.position.y = 0.75; g.add(top);
        [[-0.7, -0.35], [0.7, -0.35], [-0.7, 0.35], [0.7, 0.35]].forEach(([x, z]) => {
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.75, 8), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.7) }));
            leg.position.set(x, 0.375, z); g.add(leg);
        });
        return g;
    },
    side_table(color) {
        const g = new THREE.Group(), ci = hexInt(color);
        const top = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.03, 16), new THREE.MeshPhongMaterial({ color: ci }));
        top.position.y = 0.55; g.add(top);
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.04, 0.55, 8), new THREE.MeshPhongMaterial({ color: darkenHex(color, 0.7) }));
        pole.position.y = 0.275; g.add(pole);
        return g;
    },
    plant() {
        const g = new THREE.Group();
        const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.12, 0.25, 8), new THREE.MeshPhongMaterial({ color: 0x8B4513 }));
        pot.position.y = 0.125; g.add(pot);
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.03, 0.3, 6), new THREE.MeshPhongMaterial({ color: 0x654321 }));
        trunk.position.y = 0.3; g.add(trunk);
        const foliage = new THREE.Mesh(new THREE.SphereGeometry(0.25, 12, 12), new THREE.MeshPhongMaterial({ color: 0x228B22 }));
        foliage.position.y = 0.5; g.add(foliage);
        return g;
    },
    mirror() {
        const g = new THREE.Group();
        const frame = new THREE.Mesh(new THREE.BoxGeometry(0.65, 1.25, 0.06), new THREE.MeshPhongMaterial({ color: 0x555555 }));
        frame.position.y = 0.9; g.add(frame);
        const m = new THREE.Mesh(new THREE.BoxGeometry(0.55, 1.15, 0.02), new THREE.MeshPhongMaterial({ color: 0xE8E8FF, specular: 0xffffff, shininess: 100, side: THREE.DoubleSide }));
        m.position.set(0, 0.9, 0.035); g.add(m);
        return g;
    }
};

const ICONS = {
    sofa: '🛋️', table: '☕', chair: '🪑', bed: '🛏️', wardrobe: '🚪',
    bookshelf: '📚', lamp: '💡', desk: '🖥️', rug: '🟪',
    tv_stand: '📺', dining_table: '🍽️', side_table: '🪵', plant: '🌿', mirror: '🪞'
};

// ============================================================
// Inline model definitions (self-contained, no API needed)
// ============================================================
const INLINE_MODELS = {
    sofa: { name: 'Sofa', color: '#6366f1', description: 'Three-seater sofa' },
    table: { name: 'Coffee Table', color: '#92400e', description: 'Modern coffee table' },
    chair: { name: 'Chair', color: '#7c3aed', description: 'Dining chair' },
    bed: { name: 'Bed', color: '#1e40af', description: 'Queen-size bed' },
    wardrobe: { name: 'Wardrobe', color: '#78350f', description: 'Two-door wardrobe' },
    bookshelf: { name: 'Bookshelf', color: '#92400e', description: 'Five-tier bookshelf' },
    lamp: { name: 'Floor Lamp', color: '#f59e0b', description: 'Modern floor lamp' },
    desk: { name: 'Study Desk', color: '#78350f', description: 'Work desk' },
    rug: { name: 'Area Rug', color: '#6b7280', description: 'Decorative rug' },
    tv_stand: { name: 'TV Stand', color: '#1f2937', description: 'Entertainment unit' },
    dining_table: { name: 'Dining Table', color: '#78350f', description: 'Six-seater table' },
    side_table: { name: 'Side Table', color: '#6b7280', description: 'Bedside table' },
    plant: { name: 'Indoor Plant', color: '#15803d', description: 'Decorative plant' },
    mirror: { name: 'Mirror', color: '#475569', description: 'Full-length mirror' }
};

// Per-room-type AI recommendation defaults
const ROOM_DEFAULTS = {
    living_room: ['sofa', 'table', 'tv_stand', 'lamp', 'rug', 'plant'],
    bedroom: ['bed', 'wardrobe', 'side_table', 'lamp', 'mirror'],
    kitchen: ['dining_table', 'chair', 'lamp'],
    dining_room: ['dining_table', 'chair', 'lamp', 'rug', 'mirror'],
    office: ['desk', 'chair', 'bookshelf', 'lamp', 'plant'],
    bathroom: ['mirror', 'plant', 'lamp']
};

// ============================================================
// Scene Setup
// ============================================================
function initScene() {
    const canvas = document.getElementById('studio-canvas');
    const wrapper = document.getElementById('canvasWrapper');

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0d0d1f);
    // No fog — room walls must stay visible at all distances

    camera = new THREE.PerspectiveCamera(65, wrapper.clientWidth / wrapper.clientHeight, 0.1, 200);
    // Camera INSIDE the room, looking toward the front wall
    camera.position.set(0, 2.5, 2);
    camera.lookAt(0, 1.5, -2);

    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setSize(wrapper.clientWidth, wrapper.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    // Use NoToneMapping so MeshBasicMaterial textures display at full brightness
    renderer.toneMapping = THREE.NoToneMapping;
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 1.5;
    controls.minDistance = 0.3;
    controls.maxDistance = 7;   // keep user inside the room
    controls.target.set(0, 1.5, -2);

    // ---- Lights ---- bright enough to illuminate textured walls
    scene.add(new THREE.AmbientLight(0xffffff, 1.5));

    const sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(0, 6, 0);
    sun.castShadow = true;
    sun.shadow.mapSize.width = sun.shadow.mapSize.height = 2048;
    scene.add(sun);

    const fill = new THREE.DirectionalLight(0xaabbff, 0.6);
    fill.position.set(-3, 2, 3); scene.add(fill);
    const back = new THREE.DirectionalLight(0xffeedd, 0.4);
    back.position.set(3, 2, -3); scene.add(back);

    // Floor plane removed — room box provides its own floor face

    // ---- Grid ----
    gridHelper = new THREE.GridHelper(10, 20, 0x333355, 0x222244);
    gridHelper.position.y = 0.002;
    scene.add(gridHelper);

    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    dragPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    gltfLoader = new GLTFLoader();

    buildRoomBox();
    loadPlacements();
    setupEventListeners();
    animate();
    window.addEventListener('resize', onWindowResize);

    console.log('[Studio] Init complete. faceUrls:', studioData.faceUrls);
}

// ============================================================
// 6-Face Room Box
// ============================================================
const RS = 8;   // room full-size (width/depth)
const RH = 4;   // room height

function buildRoomBox() {
    if (roomBox) {
        scene.remove(roomBox);
        roomBox.traverse(c => { if (c.isMesh) { c.geometry?.dispose(); c.material?.dispose(); } });
    }
    roomBox = new THREE.Group();
    roomBox.name = '__roombox__';

    const faceUrls = studioData.faceUrls || {};

    const faces = [
        { n: 'front', p: [0, RH / 2, -RS / 2], rx: 0, ry: 0, w: RS, h: RH },
        { n: 'back', p: [0, RH / 2, RS / 2], rx: 0, ry: 180, w: RS, h: RH },
        { n: 'left', p: [-RS / 2, RH / 2, 0], rx: 0, ry: 90, w: RS, h: RH },
        { n: 'right', p: [RS / 2, RH / 2, 0], rx: 0, ry: -90, w: RS, h: RH },
        { n: 'ceiling', p: [0, RH, 0], rx: 90, ry: 0, w: RS, h: RS },
        { n: 'floor', p: [0, 0.01, 0], rx: -90, ry: 0, w: RS, h: RS },
    ];

    const defaultColors = {
        front: 0x1e2040, back: 0x1e2040, left: 0x1a1c38,
        right: 0x1a1c38, ceiling: 0x141628, floor: 0x111122
    };

    faces.forEach(f => {
        const url = faceUrls[f.n];

        // Create mesh with default color first
        const mat = new THREE.MeshBasicMaterial({
            color: defaultColors[f.n],
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.75
        });
        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(f.w, f.h), mat);
        mesh.position.set(...f.p);
        mesh.rotation.x = THREE.MathUtils.degToRad(f.rx);
        mesh.rotation.y = THREE.MathUtils.degToRad(f.ry);
        mesh.name = `__face_${f.n}__`;
        roomBox.add(mesh);

        // Load texture asynchronously
        if (url) {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = () => {
                const tex = new THREE.Texture(img);
                tex.colorSpace = THREE.SRGBColorSpace;
                tex.needsUpdate = true;
                mesh.material.dispose();
                mesh.material = new THREE.MeshBasicMaterial({
                    map: tex,
                    side: THREE.DoubleSide
                });
                console.log(`[Studio] ✅ ${f.n}: ${img.width}×${img.height}`);
            };
            img.onerror = (e) => {
                console.error(`[Studio] ❌ ${f.n}: FAILED (${url})`, e);
            };
            img.src = url;
        }
    });

    scene.add(roomBox);
}

// ============================================================
// Furniture
// ============================================================
function createFurniture(rawType, color = '#8b5cf6', pos = { x: 0, y: 0, z: 0 }, rotY = 0, scale = 1) {
    const type = resolveType(rawType);
    const generator = GEO[type];
    let group;

    if (generator) {
        group = generator(color);
    } else {
        // Generic box fallback
        const m = new THREE.Mesh(
            new THREE.BoxGeometry(0.6, 0.6, 0.6),
            new THREE.MeshPhongMaterial({ color: hexInt(color) })
        );
        m.position.y = 0.3;
        group = new THREE.Group(); group.add(m);
    }

    group.position.set(pos.x, pos.y, pos.z);
    group.rotation.y = rotY;
    group.scale.setScalar(scale);
    group.userData = { type, color, isFurniture: true };
    group.name = type;

    group.traverse(c => {
        if (c instanceof THREE.Mesh) {
            c.castShadow = true;
            c.receiveShadow = true;
        }
    });

    scene.add(group);
    furnitureObjects.push(group);
    console.log(`[Studio] Added: ${type}`);
    return group;
}

function loadPlacements() {
    (studioData.placements || []).forEach(p => {
        createFurniture(p.model_name, p.color || '#8b5cf6',
            { x: p.position_x, y: p.position_y, z: p.position_z },
            p.rotation || 0, p.scale || 1);
    });
}

// ============================================================
// Furniture List
// ============================================================
async function loadFurnitureList() {
    const list = document.getElementById('furnitureList');
    if (!list) return;

    // AI recommended — items and detailed placements
    const detailedPlacements = studioData.aiOutput?.detailed_placements || [];
    const recommendedFurniture = Array.isArray(studioData.aiOutput?.recommended_furniture)
        ? studioData.aiOutput.recommended_furniture : [];

    // Create a map for quick lookup of detailed advice
    const adviceMap = new Map();
    detailedPlacements.forEach(adv => {
        if (adv.item) adviceMap.set(resolveType(adv.item), adv);
    });

    // Fallback to defaults if both are empty
    let recList = recommendedFurniture.map(r => resolveType(r));
    if (recList.length === 0 && adviceMap.size === 0) {
        recList = ROOM_DEFAULTS[studioData.roomType] || ROOM_DEFAULTS['living_room'];
        console.log('[Studio] No AI recs — using defaults for', studioData.roomType);
    }

    // Try to fetch enhanced data from the API; fall back to INLINE_MODELS
    let modelData = { ...INLINE_MODELS };
    try {
        const res = await fetch('/api/models');
        if (res.ok) {
            const api = await res.json();
            if (api && Object.keys(api).length > 0) {
                modelData = { ...INLINE_MODELS, ...api };
            }
        }
    } catch (e) {
        console.warn('[Studio] Model fetch failed — using inline models');
    }

    let html = '';

    // ---- Group 1: Items with Detailed AI Placement Advice ----
    if (adviceMap.size > 0) {
        html += `<p style="font-size:0.72rem;color:var(--highlight);margin-bottom:0.6rem;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">✨ Recommended Placement</p>`;
        adviceMap.forEach((adv, type) => {
            const m = modelData[type] || { name: adv.item, color: '#8b5cf6', description: '' };
            html += furnitureItemHTML(type, m, true, adv); // Pass full 'adv' object
        });
        html += `<div style="height:10px;"></div>`;
    }

    // ---- Group 2: Other Suggested Items ----
    const processed = new Set(adviceMap.keys());
    const suggests = recList.filter(type => !processed.has(type));
    if (suggests.length > 0) {
        html += `<p style="font-size:0.72rem;color:var(--accent-light);margin-bottom:0.6rem;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">🪄 AI Suggestions</p>`;
        suggests.forEach(type => {
            const m = modelData[type] || { name: type, color: '#8b5cf6', description: '' };
            html += furnitureItemHTML(type, m, true);
            processed.add(type);
        });
        html += `<div style="height:10px;"></div>`;
    }

    // ---- Group 3: All Other Furniture ----
    html += `<hr style="border-color:rgba(255,255,255,0.08);margin:1rem 0;">
             <p style="font-size:0.72rem;color:var(--text-muted);margin-bottom:0.6rem;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">All Components</p>`;

    Object.entries(modelData).forEach(([type, m]) => {
        if (!processed.has(type)) html += furnitureItemHTML(type, m, false);
    });

    list.innerHTML = html;

    list.querySelectorAll('.furniture-item').forEach(item => {
        item.addEventListener('click', () => {
            const type = item.dataset.type;
            const color = item.dataset.color; // This is the AI suggested color if rec, or default if not
            const x = (Math.random() - 0.5) * 4;
            const z = (Math.random() - 0.5) * 2 - 1;
            const obj = createFurniture(type, color, { x, y: 0, z });
            if (obj) selectObject(obj);
        });
    });
}

function furnitureItemHTML(type, m, isRec, advice = null) {
    const icon = ICONS[type] || '📦';
    const color = (isRec && advice && advice.color) ? advice.color : m.color;
    const borderStyle = isRec ? `border: 2px solid ${color}; background: ${color}08;` : '';
    const badge = isRec ? `<span style="font-size:0.65rem; background:linear-gradient(90deg, ${color}, var(--highlight)); color:white; padding:3px 8px; border-radius:12px; font-weight:800; margin-left:auto; box-shadow:0 2px 10px ${color}44;">✨ AI CHOICE</span>` : '';

    // Explicit advice labels for better clarity
    const whereLabel = (advice && advice.where) ? `
        <div style="margin-top:0.8rem; padding:0.6rem; background:${color}15; border-radius:8px; border-left:4px solid ${color};">
            <div style="font-size:0.65rem; color:${color}; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.2rem;">📍 Recommended Placement</div>
            <div style="font-size:0.82rem; color:var(--text-primary); font-weight:700; line-height:1.3;">${advice.where}</div>
        </div>` : '';

    const colorLabel = isRec ? `
        <div style="margin-top:0.5rem; display:flex; align-items:center; gap:0.5rem;">
            <div style="font-size:0.65rem; color:var(--text-muted); font-weight:800; text-transform:uppercase; letter-spacing:0.05em;">🎨 Recommended Color:</div>
            <div style="display:flex; align-items:center; gap:0.4rem; background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:20px; border:1px solid rgba(255,255,255,0.1);">
                <span style="width:12px; height:12px; border-radius:50%; background:${color}; box-shadow:0 0 8px ${color};"></span>
                <span style="font-family:monospace; font-size:0.75rem; color:var(--highlight); font-weight:700;">${color.toUpperCase()}</span>
            </div>
        </div>` : '';

    const colorLogic = (advice && advice.color_logic) ? `<div style="font-size:0.75rem; color:var(--accent-light); margin-top:0.4rem; font-style:italic; line-height:1.4;">"Harmonizes with your room because ${advice.color_logic}"</div>` : '';
    const detailedDesc = (advice && advice.description) ? advice.description : (m.description || '');

    return `<div class="furniture-item" data-type="${type}" data-color="${color}" style="${borderStyle}; padding:1.2rem; transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);">
        <div class="furniture-preview" style="background:${color}20; color:${color}; font-size:1.8rem; display:flex; align-items:center; justify-content:center; border-radius:12px;">${icon}</div>
        <div style="flex:1;">
            <div style="display:flex; align-items:center; width:100%; margin-bottom:0.4rem;">
                <div class="furniture-name" style="font-size:1.1rem; font-weight:800; color:var(--text-primary);">${m.name || type.replace(/_/g, ' ')}</div>
                ${badge}
            </div>
            
            <div class="furniture-desc" style="font-size:0.8rem; color:var(--text-muted); line-height:1.4;">${detailedDesc}</div>
            
            ${colorLabel}
            ${colorLogic}
            ${whereLabel}
            
            ${advice && advice.why ? `<div style="font-size:0.72rem; color:var(--text-muted); font-style:italic; margin-top:0.8rem; border-top:1px solid rgba(255,255,255,0.08); padding-top:0.6rem; display:flex; gap:0.3rem;">
                <span>💡</span> <span>Reason: ${advice.why}</span>
            </div>` : ''}
        </div>
    </div>`;
}

// ============================================================
// Selection
// ============================================================
function selectObject(obj) {
    if (selectedObject) {
        selectedObject.traverse(c => {
            if (c instanceof THREE.Mesh && c.material?.emissive) {
                c.material.emissive.setHex(0x000000);
                c.material.emissiveIntensity = 0;
            }
        });
    }
    selectedObject = obj;
    if (obj) {
        obj.traverse(c => {
            if (c instanceof THREE.Mesh && c.material?.emissive !== undefined) {
                c.material.emissive = new THREE.Color(0x8b5cf6);
                c.material.emissiveIntensity = 0.35;
            }
        });
        const nm = document.getElementById('selectedName');
        if (nm) nm.textContent = (ICONS[obj.userData.type] || '📦') + ' ' + (obj.userData.type || '').replace(/_/g, ' ');
        updatePosDisplay();
        const info = document.getElementById('selectedInfo');
        if (info) info.style.opacity = '1';
    } else {
        const info = document.getElementById('selectedInfo');
        if (info) info.style.opacity = '0.4';
        const nm = document.getElementById('selectedName');
        if (nm) nm.textContent = 'No object selected';
    }
}

function updatePosDisplay() {
    if (!selectedObject) return;
    const p = selectedObject.position;
    const el = document.getElementById('selectedPos');
    if (el) el.textContent = `Pos: (${p.x.toFixed(1)}, ${p.y.toFixed(1)}, ${p.z.toFixed(1)})  Scale: ${selectedObject.scale.x.toFixed(2)}×`;
}

function showSelectHint() {
    const h = document.getElementById('selectHint');
    if (!h) return;
    h.style.display = 'block';
    clearTimeout(h._t);
    h._t = setTimeout(() => { h.style.display = 'none'; }, 2200);
}

// ============================================================
// Mouse / Touch / Keyboard
// ============================================================
function setMouseFromEvent(e) {
    const r = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - r.left) / r.width) * 2 - 1;
    mouse.y = -((e.clientY - r.top) / r.height) * 2 + 1;
}

function hitFurniture() {
    raycaster.setFromCamera(mouse, camera);
    const meshes = [];
    furnitureObjects.forEach(o => o.traverse(c => { if (c instanceof THREE.Mesh) meshes.push(c); }));
    const hits = raycaster.intersectObjects(meshes, false);
    if (!hits.length) return null;
    let t = hits[0].object;
    while (t.parent && !t.userData.isFurniture) t = t.parent;
    return t.userData.isFurniture ? { object: t, point: hits[0].point } : null;
}

function onMouseDown(e) {
    if (e.button !== 0) return;
    setMouseFromEvent(e);
    const hit = hitFurniture();
    if (hit) {
        isDragging = true;
        controls.enabled = false;
        selectObject(hit.object);
        const ip = new THREE.Vector3();
        raycaster.ray.intersectPlane(dragPlane, ip);
        dragOffset.subVectors(hit.object.position, ip);
    } else {
        selectObject(null);
    }
}
function onMouseMove(e) {
    if (!isDragging || !selectedObject) return;
    setMouseFromEvent(e);
    raycaster.setFromCamera(mouse, camera);
    const ip = new THREE.Vector3();
    raycaster.ray.intersectPlane(dragPlane, ip);
    selectedObject.position.x = ip.x + dragOffset.x;
    selectedObject.position.z = ip.z + dragOffset.z;
    updatePosDisplay();
}
function onMouseUp() { isDragging = false; controls.enabled = true; }
function onDblClick(e) { setMouseFromEvent(e); const h = hitFurniture(); if (h) selectObject(h.object); }

function onTouchStart(e) {
    if (e.touches.length === 1) { e.preventDefault(); onMouseDown({ clientX: e.touches[0].clientX, clientY: e.touches[0].clientY, button: 0 }); }
}
function onTouchMove(e) {
    if (e.touches.length === 1 && isDragging) { e.preventDefault(); onMouseMove({ clientX: e.touches[0].clientX, clientY: e.touches[0].clientY }); }
}
function onTouchEnd() { onMouseUp(); }

function onKeyDown(e) {
    if (!selectedObject) return;
    if (e.key === 'r' || e.key === 'R') rotateBy(Math.PI / 12);
    if (e.key === 'e' || e.key === 'E') rotateBy(-Math.PI / 12);
    if (e.key === '+' || e.key === '=') scaleBy(1.1);
    if (e.key === '-' || e.key === '_') scaleBy(0.9);
    if (e.key === 'Delete' || e.key === 'Backspace') deleteSelected();
}

// ============================================================
// Manipulation
// ============================================================
function rotateBy(angle) {
    if (!selectedObject) return;
    selectedObject.rotation.y += angle;
    updatePosDisplay();
}
function scaleBy(f) {
    if (!selectedObject) return;
    const s = selectedObject.scale.x * f;
    if (s > 0.15 && s < 6) { selectedObject.scale.setScalar(s); updatePosDisplay(); }
}
function deleteSelected() {
    if (!selectedObject) return;
    scene.remove(selectedObject);
    furnitureObjects = furnitureObjects.filter(o => o !== selectedObject);
    selectedObject.traverse(c => { if (c instanceof THREE.Mesh) { c.geometry?.dispose(); c.material?.dispose(); } });
    selectObject(null);
}
function resetScene() {
    if (!confirm('Remove all furniture from the scene?')) return;
    furnitureObjects.forEach(o => {
        scene.remove(o);
        o.traverse(c => { if (c instanceof THREE.Mesh) { c.geometry?.dispose(); c.material?.dispose(); } });
    });
    furnitureObjects = [];
    selectObject(null);
}
function toggleRoomWalls() { showRoomWalls = !showRoomWalls; if (roomBox) roomBox.visible = showRoomWalls; }
function toggleGrid() { showGrid = !showGrid; if (gridHelper) gridHelper.visible = showGrid; }
function resetCamera() {
    camera.position.set(0, 2.5, 2);
    controls.target.set(0, 1.5, -2);
    controls.update();
}

// ============================================================
// Save
// ============================================================
async function savePlacements() {
    const btn = document.getElementById('btnSave');
    btn.textContent = '⏳ Saving…';
    btn.disabled = true;
    const placements = furnitureObjects.map(o => ({
        model_name: o.userData.type || o.name,
        position_x: o.position.x, position_y: o.position.y, position_z: o.position.z,
        rotation: o.rotation.y, scale: o.scale.x,
        color: o.userData.color || '#8b5cf6'
    }));
    try {
        const r = await fetch(`/api/design/${studioData.designId}/placements`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ placements })
        });
        const d = await r.json();
        if (r.ok) {
            btn.textContent = '✅ Saved!';
            setTimeout(() => { btn.textContent = '💾 Save Design'; btn.disabled = false; }, 2000);
        } else throw new Error(d.error || 'Save failed');
    } catch (err) {
        btn.textContent = '❌ Error';
        setTimeout(() => { btn.textContent = '💾 Save Design'; btn.disabled = false; }, 2000);
        alert('Save failed: ' + err.message);
    }
}

// ============================================================
// Voice
// ============================================================
function appendVoiceMsg(text, who) {
    const msgs = document.getElementById('voiceMessages');
    if (!msgs) return;
    const div = document.createElement('div');
    div.className = `voice-message ${who === 'user' ? 'user-msg' : 'bot-msg'}`;
    div.textContent = text;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
}
async function sendVoice() {
    const input = document.getElementById('voiceInput');
    const q = input?.value.trim();
    if (!q) return;
    appendVoiceMsg(q, 'user');
    if (input) input.value = '';
    try {
        const r = await fetch('/api/voice-assist', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: q })
        });
        const d = await r.json();
        appendVoiceMsg(d.text || 'No response.', 'bot');
    } catch { appendVoiceMsg('Voice assistant unavailable.', 'bot'); }
}

// ============================================================
// Event Wiring
// ============================================================
function setupEventListeners() {
    const cv = renderer.domElement;
    cv.addEventListener('mousedown', onMouseDown);
    cv.addEventListener('mousemove', onMouseMove);
    cv.addEventListener('mouseup', onMouseUp);
    cv.addEventListener('dblclick', onDblClick);
    cv.addEventListener('touchstart', onTouchStart, { passive: false });
    cv.addEventListener('touchmove', onTouchMove, { passive: false });
    cv.addEventListener('touchend', onTouchEnd);
    document.addEventListener('keydown', onKeyDown);

    function guard(fn) {
        return () => { if (!selectedObject) { showSelectHint(); return; } fn(); };
    }

    document.getElementById('btnRotateLeft')?.addEventListener('click', guard(() => rotateBy(-Math.PI / 12)));
    document.getElementById('btnRotateRight')?.addEventListener('click', guard(() => rotateBy(Math.PI / 12)));
    document.getElementById('btnScaleUp')?.addEventListener('click', guard(() => scaleBy(1.1)));
    document.getElementById('btnScaleDown')?.addEventListener('click', guard(() => scaleBy(0.9)));
    document.getElementById('btnDelete')?.addEventListener('click', guard(deleteSelected));
    document.getElementById('btnReset')?.addEventListener('click', resetScene);
    document.getElementById('btnSave')?.addEventListener('click', savePlacements);
    document.getElementById('btnToggleBg')?.addEventListener('click', toggleRoomWalls);
    document.getElementById('btnResetCamera')?.addEventListener('click', resetCamera);
    document.getElementById('btnGrid')?.addEventListener('click', toggleGrid);

    const vToggle = document.getElementById('voiceToggle');
    const vPanel = document.getElementById('voicePanel');
    const vClose = document.getElementById('closeVoicePanel');
    const vSend = document.getElementById('voiceSend');
    const vInput = document.getElementById('voiceInput');
    vToggle?.addEventListener('click', () => { vPanel.style.display = vPanel.style.display === 'flex' ? 'none' : 'flex'; });
    vClose?.addEventListener('click', () => { vPanel.style.display = 'none'; });
    vSend?.addEventListener('click', sendVoice);
    vInput?.addEventListener('keydown', e => { if (e.key === 'Enter') sendVoice(); });
}

// ============================================================
// Resize + Render
// ============================================================
function onWindowResize() {
    const w = document.getElementById('canvasWrapper');
    camera.aspect = w.clientWidth / w.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(w.clientWidth, w.clientHeight);
}
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// ============================================================
// Amazon Product Recommendations (Tavily Search)
// ============================================================
async function loadProductRecommendations() {
    const section = document.getElementById('productRecsSection');
    const list = document.getElementById('productRecsList');
    if (!section || !list) return;

    // Gather recommended furniture types
    const detailedPlacements = studioData.aiOutput?.detailed_placements || [];
    const recommendedFurniture = Array.isArray(studioData.aiOutput?.recommended_furniture)
        ? studioData.aiOutput.recommended_furniture : [];

    let items = [];

    // Collect from detailed placements
    detailedPlacements.forEach(adv => {
        if (adv.item) items.push(adv.item);
    });

    // Collect from recommended furniture
    recommendedFurniture.forEach(r => {
        const name = r.replace(/_/g, ' ');
        if (!items.some(i => i.toLowerCase() === name.toLowerCase())) {
            items.push(name);
        }
    });

    // Fallback to room defaults
    if (items.length === 0) {
        const defaults = {
            living_room: ['sofa', 'coffee table', 'floor lamp'],
            bedroom: ['bed', 'wardrobe', 'side table'],
            kitchen: ['dining table', 'chair'],
            office: ['desk', 'chair', 'bookshelf']
        };
        items = defaults[studioData.roomType] || ['sofa', 'table', 'lamp'];
    }

    // Limit to 6 items max
    items = items.slice(0, 6);
    const style = studioData.style || 'modern';

    section.style.display = 'block';
    list.innerHTML = '<div class="spinner"></div>';

    let allProductsHTML = '';
    let loadedCount = 0;

    for (const item of items) {
        try {
            const res = await fetch('/api/product-search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: item, style })
            });

            if (!res.ok) continue;
            const data = await res.json();

            if (data.products && data.products.length > 0) {
                // Show category header
                allProductsHTML += `
                    <div style="padding:0.4rem 0.6rem;background:linear-gradient(90deg,rgba(255,153,0,0.12),transparent);
                        border-radius:8px;margin-top:${loadedCount > 0 ? '0.6rem' : '0'};">
                        <span style="font-size:0.75rem;font-weight:800;color:#ff9900;text-transform:uppercase;
                            letter-spacing:0.06em;">📦 ${item.replace(/_/g, ' ')}</span>
                    </div>`;

                // Show top 3 products per item
                data.products.slice(0, 3).forEach(product => {
                    const imgHTML = product.image
                        ? `<img src="${product.image}" alt="" style="width:52px;height:52px;object-fit:cover;border-radius:8px;
                            border:1px solid rgba(255,255,255,0.08);flex-shrink:0;"
                            onerror="this.style.display='none'">`
                        : `<div style="width:52px;height:52px;background:rgba(255,153,0,0.1);border-radius:8px;
                            display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0;">🛍️</div>`;

                    const truncTitle = product.title.length > 70 ? product.title.substring(0, 70) + '…' : product.title;
                    const truncSnippet = product.snippet.length > 100 ? product.snippet.substring(0, 100) + '…' : product.snippet;

                    allProductsHTML += `
                        <div style="display:flex;gap:0.7rem;align-items:flex-start;padding:0.7rem;
                            background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
                            border-radius:10px;transition:all 0.25s ease;cursor:pointer;"
                            onmouseover="this.style.background='rgba(255,153,0,0.06)';this.style.borderColor='rgba(255,153,0,0.25)'"
                            onmouseout="this.style.background='rgba(255,255,255,0.02)';this.style.borderColor='rgba(255,255,255,0.05)'"
                            onclick="window.open('${product.url}', '_blank')">
                            ${imgHTML}
                            <div style="flex:1;min-width:0;">
                                <div style="font-size:0.82rem;font-weight:700;color:#e0e0e0;line-height:1.3;margin-bottom:0.25rem;
                                    overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">
                                    ${truncTitle}
                                </div>
                                <div style="font-size:0.7rem;color:#888;line-height:1.3;margin-bottom:0.4rem;">
                                    ${truncSnippet}
                                </div>
                                <div style="display:flex;align-items:center;gap:0.5rem;">
                                    <span style="font-size:0.65rem;color:#ff9900;font-weight:700;background:rgba(255,153,0,0.1);
                                        padding:2px 8px;border-radius:12px;">${product.source}</span>
                                    <a href="${product.url}" target="_blank" rel="noopener"
                                        style="font-size:0.65rem;color:#67e8f9;text-decoration:none;font-weight:600;margin-left:auto;"
                                        onclick="event.stopPropagation()">
                                        View →
                                    </a>
                                </div>
                            </div>
                        </div>`;
                });

                loadedCount++;
            }
        } catch (err) {
            console.warn(`[Studio] Product search failed for "${item}":`, err);
        }
    }

    if (allProductsHTML) {
        list.innerHTML = allProductsHTML;
    } else {
        list.innerHTML = `<div style="text-align:center;color:#666;font-size:0.8rem;padding:1rem;">
            No products found. Try a different room style.</div>`;
    }
}

// ============================================================
// Boot
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initScene();
    loadFurnitureList();
    loadProductRecommendations();
});
