import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="T-Rex Runner: Day/Night & Music",
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

st.title("🦖 Chrome Dino: Âm Nhạc & Ngày Đêm")
st.caption("🎵 **Nhạc nền 8-bit**: Tự động phát khi chơi | ☀️/🌙 **Chu kỳ**: Đổi Ngày/Đêm mỗi 100 điểm | 🔊 Có nút Bật/Tắt nhạc")

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
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 14px;
    cursor: pointer;
    z-index: 10;
  }
  #touchHint {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 11px;
    pointer-events: none;
  }
</style>
</head>
<body>

<div id="container">
  <button id="soundBtn">🔊 Bật âm thanh</button>
  <canvas id="gameCanvas" width="800" height="270"></canvas>
  <div id="touchHint">Chạm vào màn hình hoặc bấm Space để nhảy</div>
</div>

<script>
// --- HỆ THỐNG ÂM THANH & NHẠC NỀN 8-BIT RETRO ---
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;
let isMuted = false;
let bgmInterval = null;
let bgmStep = 0;

// Giai điệu nhạc nền Chiptune vui nhộn (tần số nốt nhạc Hz)
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
    osc.type = 'triangle'; // Âm sắc ấm của game 8-bit
    const freq = melody[bgmStep % melody.length];
    bgmStep++;

    const now = audioCtx.currentTime;
    osc.frequency.setValueAtTime(freq, now);

    // Âm lượng nhẹ nhàng cho nền
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
  bgmInterval = setInterval(playBGMNote, 180); // Nhịp điệu ~166 BPM
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

// Nút tắt/bật âm thanh
const soundBtn = document.getElementById('soundBtn');
soundBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  ensureAudio();
  isMuted = !isMuted;
  soundBtn.innerText = isMuted ? '🔇 Tắt âm thanh' : '🔊 Bật âm thanh';
  if (isMuted) stopBGM();
  else if (!gameOver) startBGM();
});

// --- BIẾN VÀ CẤU HÌNH GAME ---
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

// Hệ thống Ngày / Đêm
let isNight = false;
let nightProgress = 0;

// Khủng long T-Rex
const dino = {
  x: 50,
  y: GROUND_Y - 44,
  w: 44,
  h: 44,
  vy: 0,
  gravity: 0.95,
  jumpPower: -15,
  grounded: true,
  legStep: 0
};

// Phong cảnh: Mây & Đàn chim bay trên cao
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

// Ngôi sao ban đêm
let stars = [];
for (let i = 0; i < 35; i++) {
  stars.push({
    x: Math.random() * 800,
    y: Math.random() * 140,
    size: Math.random() * 2 + 1,
    twinkle: Math.random() * Math.PI
  });
}

// Gờ đất sỏi
let groundBumps = [];
for (let i = 0; i < 800; i += 28) {
  groundBumps.push({ x: i, len: 10 + Math.random() * 16 });
}

// Chướng ngại vật
let obstacles = [];
let nextObstacleTimer = 65;

function resetGame() {
  dino.y = GROUND_Y - 44;
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

function spawnObstacle() {
  const rand = Math.random();
  // Chim pterodactyl xuất hiện khi điểm > 100
  if (score > 100 && rand < 0.4) {
    let birdY;
    const tier = Math.random();
    if (tier < 0.45) birdY = GROUND_Y - 30; // Bay sát đất
    else if (tier < 0.8) birdY = GROUND_Y - 55; // Tầm vừa
    else birdY = GROUND_Y - 80; // Tầm cao

    obstacles.push({
      type: 'pterodactyl',
      x: canvas.width + 25,
      y: birdY,
      w: 42,
      h: 28,
      wingState: 0
    });
  } else if (rand < 0.72) {
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

// --- VẼ CÁC ĐỐI TƯỢNG SPRITE ---
function drawDino(x, y, color) {
  ctx.fillStyle = color;
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
  ctx.fillRect(x + 8, y + 10, 22, 10);
  ctx.fillRect(x, y + 12, 8, 4);
  ctx.fillRect(x + 28, y + 12, 10, 6);
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

// --- CẬP NHẬT GAME ENGINE ---
function update() {
  if (gameOver) return;

  frameCount++;
  if (frameCount % 6 === 0) {
    dino.legStep = dino.legStep === 0 ? 1 : 0;
  }

  // Tăng tốc dần theo điểm số
  gameSpeed = baseSpeed + Math.min(score / 150, 8);

  // ĐỔI NGÀY / ĐÊM MỖI 100 ĐIỂM
  const cycle = Math.floor(score / 100);
  isNight = (cycle % 2 === 1);

  // Hiệu ứng chuyển màu mượt mà
  if (isNight && nightProgress < 1) nightProgress = Math.min(1, nightProgress + 0.025);
  if (!isNight && nightProgress > 0) nightProgress = Math.max(0, nightProgress - 0.025);

  // Vật lý nhảy
  dino.vy += dino.gravity;
  dino.y += dino.vy;
  if (dino.y >= GROUND_Y - dino.h) {
    dino.y = GROUND_Y - dino.h;
    dino.vy = 0;
    dino.grounded = true;
  }

  // Mây và Đàn chim trên cao
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

  // Mặt đất
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

  // Va chạm
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
      // Kêu chuông mỗi khi đạt mốc 100 điểm đổi chu kỳ
      if (score > 0 && score % 100 === 0) {
        playSound('milestone');
      }
    }
  }
}

// --- RENDER HÌNH ẢNH ---
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

  // Mặt trời / Mặt trăng & Sao
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

  // Mây & Chim trời
  clouds.forEach(c => drawCloud(c.x, c.y, cloudColor));
  skyBirds.forEach(b => drawSkyBird(b.x, b.y, b.wing, skyBirdColor));

  // Đường chạy
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

  // Nhân vật & Chướng ngại vật
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

  // Bảng điểm
  ctx.fillStyle = primaryColor;
  ctx.font = 'bold 15px "Courier New", monospace';
  ctx.textAlign = 'right';
  const cycleTag = isNight ? '🌙 ĐÊM' : '☀️ NGÀY';
  ctx.fillText(`${cycleTag}  HI ${highScore.toString().padStart(5, '0')}  ${score.toString().padStart(5, '0')}`, canvas.width - 20, 30);

  // Màn hình thua
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

// --- ĐIỀU KHIỂN ---
function handleJump() {
  ensureAudio();
  if (gameOver) {
    resetGame();
  } else if (dino.grounded) {
    dino.vy = dino.jumpPower;
    dino.grounded = false;
    playSound('jump');
    startBGM(); // Tự động phát nhạc nền khi người chơi bắt đầu
  }
}

window.addEventListener('keydown', (e) => {
  if (e.code === 'Space' || e.code === 'ArrowUp') {
    e.preventDefault();
    handleJump();
  }
});

const container = document.getElementById('container');
container.addEventListener('touchstart', (e) => {
  if (e.target.id === 'soundBtn') return;
  e.preventDefault();
  handleJump();
}, { passive: false });

container.addEventListener('mousedown', (e) => {
  if (e.target.id === 'soundBtn') return;
  handleJump();
});

gameLoop();
</script>
</body>
</html>
"""

components.html(dino_full_code, height=310)
