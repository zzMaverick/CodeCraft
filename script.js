// Smooth scroll
function smoothScroll(target) {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth'
    });
}

// Image Comparison Slider
const imageComparison = document.getElementById('imageComparison');
const slider = document.getElementById('comparisonSlider');
const processed = imageComparison.querySelector('.processed');

let isDragging = false;

slider.addEventListener('mousedown', () => {
    isDragging = true;
});

document.addEventListener('mouseup', () => {
    isDragging = false;
});

document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    
    const rect = imageComparison.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    
    if (percentage >= 0 && percentage <= 100) {
        slider.style.left = percentage + '%';
        processed.style.clipPath = `polygon(${percentage}% 0, 100% 0, 100% 100%, ${percentage}% 100%)`;
    }
});

// File Upload Demo
const fileInput = document.getElementById('fileInput');
const uploadContent = document.getElementById('uploadContent');
const processingContent = document.getElementById('processingContent');
const resultContent = document.getElementById('resultContent');
const uploadArea = document.getElementById('uploadArea');

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#059669';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#e5e7eb';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#e5e7eb';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    if (!file.name.endsWith('.nc')) {
        alert('Por favor, envie um arquivo NetCDF (.nc)');
        return;
    }
    
    startProcessing();
}

function startProcessing() {
    uploadContent.style.display = 'none';
    processingContent.style.display = 'block';
    
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const steps = ['step1', 'step2', 'step3', 'step4'];
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += 5;
        progressFill.style.width = progress + '%';
        
        if (progress === 25) {
            progressText.textContent = 'Extraindo bandas espectrais...';
            document.getElementById('step2').innerHTML = '✓ Processando 224 bandas...';
        } else if (progress === 50) {
            progressText.textContent = 'Aplicando modelo de deep learning...';
            document.getElementById('step3').innerHTML = '✓ Aplicando modelo...';
        } else if (progress === 75) {
            progressText.textContent = 'Gerando mapa de anomalias...';
            document.getElementById('step4').innerHTML = '✓ Gerando mapa de anomalias...';
        } else if (progress >= 100) {
            clearInterval(interval);
            showResults();
        }
    }, 150);
}

function showResults() {
    setTimeout(() => {
        processingContent.style.display = 'none';
        resultContent.style.display = 'block';
        
        // Simula resultados aleatórios
        const highRisk = (Math.random() * 5 + 2).toFixed(1);
        const mediumRisk = (Math.random() * 10 + 5).toFixed(1);
        const lowRisk = (100 - parseFloat(highRisk) - parseFloat(mediumRisk)).toFixed(1);
        
        document.getElementById('highRisk').textContent = highRisk + '%';
        document.getElementById('mediumRisk').textContent = mediumRisk + '%';
        document.getElementById('lowRisk').textContent = lowRisk + '%';
    }, 500);
}

function resetDemo() {
    resultContent.style.display = 'none';
    uploadContent.style.display = 'block';
    fileInput.value = '';
    
    // Reset processing steps
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('step2').innerHTML = '⏳ Processando 224 bandas...';
    document.getElementById('step3').innerHTML = '⏳ Aplicando modelo...';
    document.getElementById('step4').innerHTML = '⏳ Gerando mapa de anomalias...';
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(6, 78, 59, 1)';
    } else {
        navbar.style.background = 'rgba(6, 78, 59, 0.95)';
    }
});
