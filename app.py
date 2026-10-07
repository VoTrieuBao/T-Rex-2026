import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="T-Rex Runner: Duck & Jump Edition",
    page_icon="🦖",
    layout="wide"
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 920px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🦖 Chrome Dino: Nhảy & Cúi Người")
st.caption("💻 **Máy tính**: `Space`/`↑` để nhảy, **giữ `↓` hoặc `S` để cúi** | 📱 **Điện thoại**: Chạm để nhảy, **giữ nút 👇 để cúi**")

dino_full_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
  * {
    box-sizing: border-box;
    user-select: none;
    -webkit-user-select: none;
  }
  body {
    margin: 0;
    padding: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  #container {
    width: 100%;
    max-width: 820px;
    position: relative;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    overflow: hidden;
    touch-action: manipulation;
  }
  canvas {
    display: block;
    width: 100%;
    height: auto;
  }
  #soundBtn {
    position: absolute;
    top: 10px;
    left: 12px;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 13px;
    cursor: pointer;
    z-index: 10;
  }
  /* Nút cúi cho điện thoại */
  #duckBtn {
    position: absolute;
    bottom: 15px;
    right: 15px;
    background: rgba(30, 41, 59, 0.85);
    color: #fff;
    border: 2px solid #94a3b8;
    border-radius: 50px;
    padding: 10px 18px;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
    z-index: 10;
    display: flex;
    align-items: center;
    gap: 4px;
    touch-action: none;
  }
  #duckBtn:active {
    background: #0284c7;
  }
  #touchHint {
    position: absolute;
    bottom: 8px;
    left: 40%;
    transform: translateX(-50%);
    font-size: 11px;
    pointer-events: none;
  }
</style>
</head>
<body>

<div id="container">
  <button id="soundBtn">🔊 Bật âm thanh</button>
  <button id="duckBtn">👇 Cúi</button>
  <canvas id="gameCanvas" width="800" height="270"></canvas>
  <div id="touchHint">Space / Chạm để nhảy - Giữ Mũi tên xuống / Nút 👇 để cúi</div>
</div>

<script>
// --- ÂM THANH & BGM 8-BIT ---
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;
let isMuted = false;
let bgmInterval = null;
let bgmStep = 0;

const melody = [
  261.63, 293.66, 329.63, 392.00, 329.63, 392.00, 523.25, 392.00,
  261.63, 293.66, 329.63, 349.23, 329.63, 293.66, 261.63, 196.00,
  220.00, 261.63, 329.63, 440.00, 392.00, 329.63, 293.66, 261.63,
  196.00, 246.94, 293.66, 392.00, 349.23, 329.63, 293.66, 246.94
];

function ensureAudio() {
  if (!audioCtx) audioCtx = new AudioCtx();
  if (audioCtx.state === 'suspended') audioCtx.resume();
}

function playBGMNote() {
  if (isMuted || !audioCtx || gameOver) return;
  try {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'triangle';
    const freq = melody[bgmStep % melody.length];
    bgmStep++;

    const now = audioCtx.currentTime;
    osc.frequency.setValueAtTime(freq, now);
    gain.gain.setValueAtTime(0.04, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);

    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.18);
  } catch(e) {}
}

function startBGM() {
  if (bgmInterval) return;
  bgmInterval = setInterval(playBGMNote, 180);
}

function stopBGM() {
  if (bgmInterval) {
    clearInterval(bgmInterval);
    bgmInterval = null;
  }
}

function playSound(type) {
  if (isMuted) return;
  try {
    ensureAudio();
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    const now = audioCtx.currentTime;

    if (type === 'jump') {
      osc.type = 'square';
      osc.frequency.setValueAtTime(150, now);
      osc.frequency.exponentialRampToValueAtTime(560, now + 0.12);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
      osc.start(now);
      osc.stop(now + 0.12);
    } else if (type === 'die') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(300, now);
      osc.frequency.exponentialRampToValueAtTime(50, now + 0.35);
      gain.gain.setValueAtTime(0.22, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.start(now);
      osc.stop(now + 0.35);
    } else if (type === 'milestone') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587, now);
      osc.frequency.setValueAtTime(880, now + 0.08);
      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      osc.start(now);
      osc.stop(now + 0.25);
    }
  } catch(e) {}
}

const soundBtn = document.getElementById('soundBtn');
soundBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  ensureAudio();
  isMuted = !isMuted;
  soundBtn.innerText = isMuted ? '🔇 Tắt âm thanh' : '🔊 Bật âm thanh';
  if (isMuted) stopBGM();
  else if (!gameOver) startBGM();
});

// --- CẤU HÌNH GAME ---
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const touchHint = document.getElementById('touchHint');

const GROUND_Y = 225;
let baseSpeed = 6;
let gameSpeed = 6;
let score = 0;
let highScore = 0;
let gameOver = false;
let frameCount = 0;

let isNight = false;
let nightProgress = 0;

// Khủng long hỗ trợ cúi người
const dino = {
  x: 50,
  y: GROUND_Y - 44,
  w: 44,
  h: 44,
  standHeight: 44,
  standWidth: 44,
  duckHeight: 26,
  duckWidth: 56,
  isDucking: false,
  vy: 0,
  gravity: 0.95,
  jumpPower: -15,
  grounded: true,
  legStep: 0
};

let clouds = [
  { x: 180, y: 45, speed: 0.6 },
  { x: 490, y: 70, speed: 0.5 },
  { x: 740, y: 35, speed: 0.7 }
];

let skyBirds = [
  { x: 260, y: 35, speed: 1.2, wing: 0 },
  { x: 580, y: 55, speed: 1.0, wing: 1 },
  { x: 800, y: 25, speed: 1.3, wing: 0 }
];

let stars = [];
for (let i = 0; i < 35; i++) {
  stars.push({
    x: Math.random() * 800,
    y: Math.random() * 140,
    size: Math.random() * 2 + 1,
    twinkle: Math.random() * Math.PI
  });
}

let groundBumps = [];
for (let i = 0; i < 800; i += 28) {
  groundBumps.push({ x: i, len: 10 + Math.random() * 16 });
}

let obstacles = [];
let nextObstacleTimer = 65;

function resetGame() {
  dino.isDucking = false;
  dino.h = dino.standHeight;
  dino.w = dino.standWidth;
  dino.y = GROUND_Y - dino.standHeight;
  dino.vy = 0;
  dino.grounded = true;
  obstacles = [];
  gameSpeed = baseSpeed;
  score = 0;
  frameCount = 0;
  nextObstacleTimer = 60;
  gameOver = false;
  isNight = false;
  nightProgress = 0;
  bgmStep = 0;
  startBGM();
}

// Sinh chướng ngại vật (Thêm chim bay buộc phải cúi)
function spawnObstacle() {
  const rand = Math.random();

  if (score > 100 && rand < 0.45) {
    let birdY;
    const tier = Math.random();

    if (tier < 0.45) {
      // 1. Tầm cao ngang người (GROUND_Y - 54px): Phải cúi để vượt qua!
      birdY = GROUND_Y - 54;
    } else if (tier < 0.8) {
      // 2. Tầm sát đất: Phải nhảy
      birdY = GROUND_Y - 32;
    } else {
      // 3. Tầm bay rất cao: Có thể chạy qua bình thường
      birdY = GROUND_Y - 82;
    }

    obstacles.push({
      type: 'pterodactyl',
      x: canvas.width + 25,
      y: birdY,
      w: 44,
      h: 28,
      wingState: 0
    });
  } else if (rand < 0.75) {
    obstacles.push({
      type: 'cactus_group',
      x: canvas.width + 25,
      y: GROUND_Y - 46,
      w: 40,
      h: 46
    });
  } else {
    obstacles.push({
      type: 'cactus_single',
      x: canvas.width + 25,
      y: GROUND_Y - 40,
      w: 22,
      h: 40
    });
  }
}

// --- VẼ KHỦNG LONG: ĐỨNG VÀ CÚI ---
function drawDino(x, y, color) {
  ctx.fillStyle = color;

  if (dino.isDucking && dino.grounded) {
    // VẼ KHỦNG LONG ĐANG CÚI RẠP NGƯỜI
    // Thân dài nằm ngang
    ctx.fillRect(x + 10, y + 8, 32, 12);
    // Đầu chúc về trước
    ctx.fillRect(x + 36, y + 4, 18, 12);
    // Đuôi sau
    ctx.fillRect(x, y + 10, 10, 8);

    // Mắt
    ctx.fillStyle = isNight ? '#0f172a' : '#ffffff';
    ctx.fillRect(x + 48, y + 6, 4, 4);

    // Chân đạp khi cúi
    ctx.fillStyle = color;
    if (dino.legStep === 0) {
      ctx.fillRect(x + 16, y + 20, 5, 6);
      ctx.fillRect(x + 28, y + 20, 5, 4);
    } else {
      ctx.fillRect(x + 16, y + 20, 5, 4);
      ctx.fillRect(x + 28, y + 20, 5, 6);
    }
  } else {
    // VẼ KHỦNG LONG ĐỨNG BÌNH THƯỜNG
    ctx.fillRect(x + 16, y + 2, 22, 14); // Đầu
    ctx.fillRect(x + 12, y + 14, 20, 18); // Thân
    ctx.fillRect(x + 4, y + 18, 10, 10); // Đuôi

    // Mắt
    ctx.fillStyle = isNight ? '#0f172a' : '#ffffff';
    ctx.fillRect(x + 30, y + 5, 4, 4);

    // Tay
    ctx.fillStyle = color;
    ctx.fillRect(x + 32, y + 20, 6, 3);

    // Chân
    if (!dino.grounded) {
      ctx.fillRect(x + 14, y + 32, 4, 10);
      ctx.fillRect(x + 24, y + 32, 4, 8);
    } else {
      if (dino.legStep === 0) {
        ctx.fillRect(x + 14, y + 32, 4, 12);
        ctx.fillRect(x + 24, y + 32, 4, 6);
      } else {
        ctx.fillRect(x + 14, y + 32, 4, 6);
        ctx.fillRect(x + 24, y + 32, 4, 12);
      }
    }
  }
}

function drawCactus(x, y, w, h, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x + w * 0.35, y, w * 0.3, h);
  ctx.fillRect(x, y + h * 0.3, w * 0.35, h * 0.15);
  ctx.fillRect(x, y + h * 0.15, w * 0.15, h * 0.2);
  ctx.fillRect(x + w * 0.65, y + h * 0.4, w * 0.35, h * 0.15);
  ctx.fillRect(x + w * 0.85, y + h * 0.25, w * 0.15, h * 0.2);
}

function drawPterodactyl(x, y, w, h, wing, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x + 8, y + 10, 24, 10);
  ctx.fillRect(x, y + 12, 8, 4); // Mỏ
  ctx.fillRect(x + 32, y + 12, 10, 6); // Đuôi

  if (wing === 0) ctx.fillRect(x + 14, y, 6, 12);
  else ctx.fillRect(x + 14, y + 16, 6, 12);
}

function drawSkyBird(x, y, wing, color) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.8;
  ctx.beginPath();
  if (wing === 0) {
    ctx.moveTo(x - 8, y + 4);
    ctx.quadraticCurveTo(x - 4, y - 4, x, y);
    ctx.quadraticCurveTo(x + 4, y - 4, x + 8, y + 4);
  } else {
    ctx.moveTo(x - 8, y);
    ctx.quadraticCurveTo(x - 4, y + 4, x, y);
    ctx.quadraticCurveTo(x + 4, y + 4, x + 8, y);
  }
  ctx.stroke();
}

function drawCloud(x, y, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, 14, 0, Math.PI * 2);
  ctx.arc(x + 14, y - 6, 16, 0, Math.PI * 2);
  ctx.arc(x + 30, y, 12, 0, Math.PI * 2);
  ctx.fill();
}

function drawMoon(x, y) {
  ctx.fillStyle = '#fef08a';
  ctx.beginPath();
  ctx.arc(x, y, 18, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#0f172a';
  ctx.beginPath();
  ctx.arc(x + 8, y - 4, 15, 0, Math.PI * 2);
  ctx.fill();
}

function drawSun(x, y) {
  ctx.fillStyle = '#fde047';
  ctx.beginPath();
  ctx.arc(x, y, 16, 0, Math.PI * 2);
  ctx.fill();
}

// --- CẬP NHẬT TRẠNG THÁI ---
function update() {
  if (gameOver) return;

  frameCount++;
  if (frameCount % 6 === 0) {
    dino.legStep = dino.legStep === 0 ? 1 : 0;
  }

  gameSpeed = baseSpeed + Math.min(score / 150, 8);

  // Đổi Ngày/Đêm mỗi 100 điểm
  const cycle = Math.floor(score / 100);
  isNight = (cycle % 2 === 1);
  if (isNight && nightProgress < 1) nightProgress = Math.min(1, nightProgress + 0.025);
  if (!isNight && nightProgress > 0) nightProgress = Math.max(0, nightProgress - 0.025);

  // Xử lý kích thước Hitbox khi Cúi
  if (dino.isDucking && dino.grounded) {
    dino.h = dino.duckHeight;
    dino.w = dino.duckWidth;
    dino.y = GROUND_Y - dino.duckHeight;
  } else {
    dino.h = dino.standHeight;
    dino.w = dino.standWidth;
  }

  // Nhảy và Trọng lực
  dino.vy += dino.gravity;
  dino.y += dino.vy;
  if (dino.y >= GROUND_Y - dino.h) {
    dino.y = GROUND_Y - dino.h;
    dino.vy = 0;
    dino.grounded = true;
  }

  // Mây và chim nền
  clouds.forEach(c => {
    c.x -= c.speed;
    if (c.x < -60) {
      c.x = canvas.width + 30;
      c.y = 25 + Math.random() * 65;
    }
  });

  skyBirds.forEach(b => {
    b.x -= b.speed + 0.4;
    if (frameCount % 16 === 0) b.wing = b.wing === 0 ? 1 : 0;
    if (b.x < -40) {
      b.x = canvas.width + 30 + Math.random() * 80;
      b.y = 20 + Math.random() * 55;
    }
  });

  groundBumps.forEach(g => {
    g.x -= gameSpeed;
    if (g.x < -20) g.x = canvas.width + Math.random() * 30;
  });

  // Sinh chướng ngại vật
  nextObstacleTimer--;
  if (nextObstacleTimer <= 0) {
    spawnObstacle();
    const minSpacing = Math.max(38, 65 - Math.floor(score / 80));
    nextObstacleTimer = minSpacing + Math.floor(Math.random() * 35);
  }

  // Kiểm tra va chạm
  for (let i = obstacles.length - 1; i >= 0; i--) {
    let obs = obstacles[i];
    obs.x -= gameSpeed;

    if (obs.type === 'pterodactyl' && frameCount % 10 === 0) {
      obs.wingState = obs.wingState === 0 ? 1 : 0;
    }

    const p = 5;
    if (
      dino.x + p < obs.x + obs.w - p &&
      dino.x + dino.w - p > obs.x + p &&
      dino.y + p < obs.y + obs.h - p &&
      dino.y + dino.h > obs.y + p
    ) {
      gameOver = true;
      stopBGM();
      playSound('die');
      if (score > highScore) highScore = score;
    }

    if (obs.x + obs.w < 0) {
      obstacles.splice(i, 1);
      score += 10;
      if (score > 0 && score % 100 === 0) playSound('milestone');
    }
  }
}

// --- VẼ KHUNG HÌNH ---
function draw() {
  const bgR = Math.round(248 - nightProgress * (248 - 15));
  const bgG = Math.round(250 - nightProgress * (250 - 23));
  const bgB = Math.round(252 - nightProgress * (252 - 42));
  ctx.fillStyle = `rgb(${bgR}, ${bgG}, ${bgB})`;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  touchHint.style.color = isNight ? '#94a3b8' : '#64748b';

  const primaryColor = isNight ? '#e2e8f0' : '#475569';
  const groundColor = isNight ? '#475569' : '#94a3b8';
  const cactusColor = isNight ? '#22c55e' : '#15803d';
  const birdColor = isNight ? '#f1f5f9' : '#334155';
  const skyBirdColor = isNight ? '#94a3b8' : '#64748b';
  const cloudColor = isNight ? 'rgba(51, 65, 85, 0.7)' : 'rgba(203, 213, 225, 0.8)';

  if (nightProgress > 0.1) {
    stars.forEach(s => {
      s.twinkle += 0.05;
      const alpha = (Math.sin(s.twinkle) * 0.4 + 0.6) * nightProgress;
      ctx.fillStyle = `rgba(254, 240, 138, ${alpha})`;
      ctx.fillRect(s.x, s.y, s.size, s.size);
    });
    drawMoon(710, 48);
  } else {
    drawSun(710, 45);
  }

  clouds.forEach(c => drawCloud(c.x, c.y, cloudColor));
  skyBirds.forEach(b => drawSkyBird(b.x, b.y, b.wing, skyBirdColor));

  ctx.strokeStyle = groundColor;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, GROUND_Y);
  ctx.lineTo(canvas.width, GROUND_Y);
  ctx.stroke();

  ctx.strokeStyle = isNight ? '#334155' : '#cbd5e1';
  groundBumps.forEach(g => {
    ctx.beginPath();
    ctx.moveTo(g.x, GROUND_Y + 5);
    ctx.lineTo(g.x + g.len, GROUND_Y + 5);
    ctx.stroke();
  });

  drawDino(dino.x, dino.y, primaryColor);

  obstacles.forEach(obs => {
    if (obs.type === 'pterodactyl') {
      drawPterodactyl(obs.x, obs.y, obs.w, obs.h, obs.wingState, birdColor);
    } else if (obs.type === 'cactus_group') {
      drawCactus(obs.x, obs.y, obs.w * 0.5, obs.h, cactusColor);
      drawCactus(obs.x + obs.w * 0.5, obs.y + 6, obs.w * 0.45, obs.h - 6, cactusColor);
    } else {
      drawCactus(obs.x, obs.y, obs.w, obs.h, cactusColor);
    }
  });

  ctx.fillStyle = primaryColor;
  ctx.font = 'bold 15px "Courier New", monospace';
  ctx.textAlign = 'right';
  const cycleTag = isNight ? '🌙 ĐÊM' : '☀️ NGÀY';
  ctx.fillText(`${cycleTag}  HI ${highScore.toString().padStart(5, '0')}  ${score.toString().padStart(5, '0')}`, canvas.width - 20, 30);

  if (gameOver) {
    ctx.fillStyle = isNight ? 'rgba(15, 23, 42, 0.85)' : 'rgba(255, 255, 255, 0.85)';
    ctx.fillRect(canvas.width / 2 - 170, 65, 340, 105);

    ctx.fillStyle = '#ef4444';
    ctx.font = 'bold 22px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('G A M E   O V E R', canvas.width / 2, 105);

    ctx.fillStyle = isNight ? '#cbd5e1' : '#64748b';
    ctx.font = '13px sans-serif';
    ctx.fillText('Nhấn Space hoặc chạm màn hình để chơi lại', canvas.width / 2, 138);
  }
}

function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop);
}

// --- ĐIỀU KHIỂN NHẢY & CÚI ---
function handleJump() {
  ensureAudio();
  if (gameOver) {
    resetGame();
  } else if (dino.grounded && !dino.isDucking) {
    dino.vy = dino.jumpPower;
    dino.grounded = false;
    playSound('jump');
    startBGM();
  }
}

// Bàn phím máy tính
window.addEventListener('keydown', (e) => {
  if (e.code === 'Space' || e.code === 'ArrowUp') {
    e.preventDefault();
    handleJump();
  } else if (e.code === 'ArrowDown' || e.code === 'KeyS') {
    e.preventDefault();
    ensureAudio();
    if (dino.grounded) {
      dino.isDucking = true;
    } else {
      // Nhấn mũi tên xuống khi đang bay trên không để rơi nhanh xuống đất
      dino.vy += 8;
    }
  }
});

window.addEventListener('keyup', (e) => {
  if (e.code === 'ArrowDown' || e.code === 'KeyS') {
    dino.isDucking = false;
  }
});

// Nút Cúi ảo trên điện thoại / Cảm ứng
const duckBtn = document.getElementById('duckBtn');

duckBtn.addEventListener('touchstart', (e) => {
  e.preventDefault();
  ensureAudio();
  if (dino.grounded) dino.isDucking = true;
  else dino.vy += 8;
}, { passive: false });

duckBtn.addEventListener('touchend', (e) => {
  e.preventDefault();
  dino.isDucking = false;
});

duckBtn.addEventListener('mousedown', (e) => {
  e.stopPropagation();
  ensureAudio();
  if (dino.grounded) dino.isDucking = true;
  else dino.vy += 8;
});

window.addEventListener('mouseup', () => {
  dino.isDucking = false;
});

// Chạm màn hình để nhảy
const container = document.getElementById('container');
container.addEventListener('touchstart', (e) => {
  if (e.target.id === 'soundBtn' || e.target.id === 'duckBtn') return;
  e.preventDefault();
  handleJump();
}, { passive: false });

container.addEventListener('mousedown', (e) => {
  if (e.target.id === 'soundBtn' || e.target.id === 'duckBtn') return;
  handleJump();
});

gameLoop();
</script>
</body>
</html>
"""

components.html(dino_full_code, height=330)
