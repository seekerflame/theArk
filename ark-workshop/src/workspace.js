import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export class Workspace {
    constructor(container) {
        this.container = container;
        this.scene = new THREE.Scene();
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.agents = new Map();
        this.workstations = new Map();

        this.init();
        this.createEnvironment();
        this.animate();
    }

    init() {
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            60,
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 15, 25);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setClearColor(0x0a0e1a, 1);
        this.renderer.shadowMap.enabled = true;
        this.container.appendChild(this.renderer.domElement);

        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI / 2;

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 20, 10);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);

        // Neon accent lights
        const neonGreen = new THREE.PointLight(0x00ff88, 1, 50);
        neonGreen.position.set(-10, 5, 0);
        this.scene.add(neonGreen);

        const neonPurple = new THREE.PointLight(0xaa44ff, 1, 50);
        neonPurple.position.set(10, 5, 0);
        this.scene.add(neonPurple);

        // Handle resize
        window.addEventListener('resize', () => this.onResize());
    }

    createEnvironment() {
        // Hexagonal grid floor
        this.createHexGrid();

        // Create zones for agents
        this.createAgentZone('antigravity', { x: -8, z: -8 }, 0xaa44ff);
        this.createAgentZone('business-os', { x: 8, z: -8 }, 0x00ddff);
        this.createAgentZone('user', { x: 0, z: 8 }, 0xffaa00);

        // Create workstations
        this.createWorkstation('read', { x: -10, z: 0 }, 0x00ff88);
        this.createWorkstation('write', { x: 0, z: 0 }, 0xff8844);
        this.createWorkstation('edit', { x: 10, z: 0 }, 0x4488ff);
        this.createWorkstation('terminal', { x: -5, z: -5 }, 0xff44aa);
        this.createWorkstation('search', { x: 5, z: -5 }, 0x88ff44);
    }

    createHexGrid() {
        const hexRadius = 1;
        const gridSize = 15;
        const geometry = new THREE.CircleGeometry(hexRadius, 6);
        const material = new THREE.MeshBasicMaterial({
            color: 0x00ff88,
            transparent: true,
            opacity: 0.1,
            side: THREE.DoubleSide
        });

        for (let q = -gridSize; q <= gridSize; q++) {
            for (let r = -gridSize; r <= gridSize; r++) {
                if (Math.abs(q + r) <= gridSize) {
                    const hex = new THREE.Mesh(geometry, material);
                    const x = hexRadius * (Math.sqrt(3) * q + Math.sqrt(3) / 2 * r);
                    const z = hexRadius * (3 / 2 * r);
                    hex.position.set(x, 0, z);
                    hex.rotation.x = -Math.PI / 2;
                    this.scene.add(hex);
                }
            }
        }
    }

    createAgentZone(name, position, color) {
        const zoneGroup = new THREE.Group();

        // Platform
        const platformGeometry = new THREE.CylinderGeometry(4, 4, 0.2, 32);
        const platformMaterial = new THREE.MeshStandardMaterial({
            color: color,
            transparent: true,
            opacity: 0.3,
            emissive: color,
            emissiveIntensity: 0.2
        });
        const platform = new THREE.Mesh(platformGeometry, platformMaterial);
        platform.position.y = 0.1;
        platform.receiveShadow = true;
        zoneGroup.add(platform);

        // Glowing ring
        const ringGeometry = new THREE.TorusGeometry(4, 0.1, 8, 32);
        const ringMaterial = new THREE.MeshBasicMaterial({ color: color });
        const ring = new THREE.Mesh(ringGeometry, ringMaterial);
        ring.rotation.x = Math.PI / 2;
        ring.position.y = 0.3;
        zoneGroup.add(ring);

        // Agent avatar (simple sphere for now)
        const avatarGeometry = new THREE.SphereGeometry(0.5, 32, 32);
        const avatarMaterial = new THREE.MeshStandardMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.5
        });
        const avatar = new THREE.Mesh(avatarGeometry, avatarMaterial);
        avatar.position.y = 1;
        avatar.castShadow = true;
        zoneGroup.add(avatar);

        // Label
        // (Text rendering would go here - simplified for MVP)

        zoneGroup.position.set(position.x, 0, position.z);
        this.scene.add(zoneGroup);

        this.agents.set(name, {
            group: zoneGroup,
            avatar: avatar,
            position: position,
            color: color
        });
    }

    createWorkstation(type, position, color) {
        const stationGroup = new THREE.Group();

        // Base
        const baseGeometry = new THREE.BoxGeometry(2, 1.5, 2);
        const baseMaterial = new THREE.MeshStandardMaterial({
            color: 0x1a1e2a,
            roughness: 0.4
        });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = 0.75;
        base.castShadow = true;
        stationGroup.add(base);

        // Icon (simple glowing cube for MVP)
        const iconGeometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
        const iconMaterial = new THREE.MeshStandardMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.8
        });
        const icon = new THREE.Mesh(iconGeometry, iconMaterial);
        icon.position.y = 2;
        stationGroup.add(icon);

        stationGroup.position.set(position.x, 0, position.z);
        this.scene.add(stationGroup);

        this.workstations.set(type, {
            group: stationGroup,
            position: position,
            color: color
        });
    }

    moveAgent(agentName, targetPosition, duration = 1000) {
        const agent = this.agents.get(agentName);
        if (!agent) return;

        const startPos = agent.group.position.clone();
        const endPos = new THREE.Vector3(targetPosition.x, 0, targetPosition.z);
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function
            const eased = progress < 0.5
                ? 2 * progress * progress
                : 1 - Math.pow(-2 * progress + 2, 2) / 2;

            agent.group.position.lerpVectors(startPos, endPos, eased);
            agent.avatar.position.y = 1 + Math.sin(progress * Math.PI) * 0.5; // Bounce

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    highlightWorkstation(type, duration = 2000) {
        const workstation = this.workstations.get(type);
        if (!workstation) return;

        const originalEmissive = workstation.group.children[1].material.emissive.clone();
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const pulse = Math.sin(progress * Math.PI * 4) * 0.5 + 0.5;

            workstation.group.children[1].material.emissiveIntensity = 0.8 + pulse * 0.4;

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                workstation.group.children[1].material.emissive.copy(originalEmissive);
            }
        };

        animate();
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        // Gentle rotation for all agents
        this.agents.forEach(agent => {
            agent.avatar.rotation.y += 0.01;
        });

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    onResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
}
