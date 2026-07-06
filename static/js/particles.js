(function () {
    const container = document.getElementById('particles-bg');
    if (!container) return;

    const particleCount = window.innerWidth < 768 ? 25 : 50;
    const colors = ['#6C63FF', '#FF6B6B', '#43E97B'];

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        const size = Math.random() * 3 + 1;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const startX = Math.random() * 100;
        const duration = Math.random() * 20 + 15;
        const delay = Math.random() * 20;

        particle.style.cssText = `
            position: absolute;
            left: ${startX}%;
            top: 100%;
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            border-radius: 50%;
            opacity: ${Math.random() * 0.5 + 0.2};
            box-shadow: 0 0 ${size * 3}px ${color};
            animation: floatUp ${duration}s linear ${delay}s infinite;
        `;

        container.appendChild(particle);
    }

    // Inject keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatUp {
            0% {
                transform: translateY(0) translateX(0);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-110vh) translateX(${Math.random() > 0.5 ? '' : '-'}${Math.random() * 100}px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
})();