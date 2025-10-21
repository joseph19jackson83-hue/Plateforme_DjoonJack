document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.addEventListener('mouseover', () => btn.style.backgroundColor = '#FF6600');
        btn.addEventListener('mouseout', () => btn.style.backgroundColor = 'orange');
        btn.addEventListener('click', () => console.log('Bouton cliqué !'));
    });

    const installPopup = document.createElement('div');
    installPopup.id = 'installPopup';
    installPopup.style.position = 'fixed';
    installPopup.style.bottom = '20px';
    installPopup.style.right = '20px';
    installPopup.style.background = '#FFAA00';
    installPopup.style.padding = '15px';
    installPopup.style.border = '2px solid blue';
    installPopup.style.color = '#fff';
    installPopup.style.cursor = 'pointer';
    installPopup.style.zIndex = 1000;
    installPopup.innerHTML = 'Installer l\'application Djoonjack Services';
    installPopup.onclick = () => {
        alert('Lien d\'installation cliqué !');
        installPopup.style.display = 'none';
    };
    document.body.appendChild(installPopup);

    if (typeof THREE !== 'undefined') {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({antialias: true});
        renderer.setSize(window.innerWidth, 400);
        document.getElementById('gameContainer').appendChild(renderer.domElement);

        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshBasicMaterial({color: 0x00ff00});
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
        camera.position.z = 5;

        function animate() {
            requestAnimationFrame(animate);
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            renderer.render(scene, camera);
        }
        animate();
    }
});