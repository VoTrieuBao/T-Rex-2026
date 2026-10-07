import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="T-Rex Runner: Day & Night Edition",
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

st.title("🦖 Chrome Dino: Ngày & Đêm")
st.caption("🎮 **Phím bấm**: `Space` hoặc `Mũi tên lên` | 📱 **Cảm ứng**: Chạm màn hình để nhảy | 🌙 **Chu kỳ**: Bầu trời đổi Ngày/Đêm mỗi 300 điểm")

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
    transition: background-color 1.2s ease;
  }
  #touchHint {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 11px;
    pointer-events: none;
    transition: color 1.2s ease;
  }
</style>
</head>
<body>

<div id="container">
  <canvas id="gameCanvas" width="800" height="270"></canvas>
  <div id="touchHint">Chạm vào màn hình để nhảy / chơi lại</div>
</div>

<script>
// --- ÂM THANH BẰNG WEB AUDIO API ---
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function ensureAudio() {
  if (!audioCtx) audioCtx = new AudioCtx();
  if (audioCtx.state === 'suspended') audioCtx.resume();
}

function playSound(type) {
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
      osc.frequency.exponentialRampToValueAtTime(520, now + 0.12);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
      osc.start(now);
      osc.stop(now + 0.12);
    } else if (type === 'die') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(280, now);
      osc.frequency.exponentialRampToValueAtTime(60, now + 0.32);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.32);
      osc.start(now);
      osc.stop(now + 0.32);
    } else if (type === 'milestone') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587, now);
      osc.frequency.setValueAtTime(880, now + 0.08);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      osc.start(now);
      osc.stop(now + 0.25);
    }
  } catch(e) {}
}

// --- CẤU HÌNH & TRẠNG THÁI GAME ---
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
let nightProgress = 0; // 0 = Ngày, 1 = Đêm

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

// Phong cảnh: Mây & Đàn chim bay tự do trên cao
let clouds = [
  { x: 180, y: 45, speed: 0.6 },
  { x: 490, y: 70, speed: 0.5 },
  { x: 740, y: 35, speed: 0.7 }
];

let skyBirds = [
  { x: 280, y: 35, speed: 1.2, wing: 0 },
  { x: 620, y: 50, speed: 1.0, wing: 1 },
  { x: 820, y: 25, speed: 1.3, wing: 0 }
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

// Mặt đất có gờ sỏi
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
}

function spawnObstacle() {
  const rand = Math.random();
  // Chim chướng ngại vật xuất hiện khi điểm > 150
  if (score > 150 && rand < 0.4) {
    // 3 tầng bay: Thấp sát đất, Vừa ngang người, Cao trên đầu
    let birdY;
    const heightTier = Math.random();
    if (heightTier < 0.45) {
      birdY = GROUND_Y - 30; // Buộc phải nhảy
    } else if (heightTier < 0.8) {
      birdY = GROUND_Y - 55; // Tầm vừa
    } else {
      birdY = GROUND_Y - 80; // Tầm cao
    }

    obstacles.push({
      type: 'pterodactyl',
      x: canvas.width + 25,
      y: birdY,
      w: 42,
      h: 28,
      wingState: 0
    });
  } else if (rand < 0.72) {
    // Cụm xương rồng đôi/ba
    obstacles.push({
      type: 'cactus_group',
      x: canvas.width + 25,
      y: GROUND_Y - 46,
      w: 40,
      h: 46
    });
  } else {
    // Xương rồng đơn
    obstacles.push({
      type: 'cactus_single',
      x: canvas.width + 25,
      y: GROUND_Y - 40,
      w: 22,
      h: 40
    });
  }
}

// --- HÀM VẼ SPRITE & ĐỒ HỌA ---
function drawDino(x, y, color) {
  ctx.fillStyle = color;

  // Thân, đầu & đuôi
  ctx.fillRect(x + 16, y + 2, 22, 14); // Đầu
  ctx.fillRect(x + 12, y + 14, 20, 18); // Thân
  ctx.fillRect(x + 4, y + 18, 10, 10); // Đuôi

  // Mắt
  ctx.fillStyle = isNight ? '#0f172a' : '#ffffff';
  ctx.fillRect(x + 30, y + 5, 4, 4);

  // Mũi và tay
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
  // Thân và mỏ
  ctx.fillRect(x + 8, y + 10, 22, 10);
  ctx.fillRect(x, y + 12, 8, 4);
  ctx.fillRect(x + 28, y + 12, 10, 6);

  // Cánh vỗ
  if (wing === 0) {
    ctx.fillRect(x + 14, y, 6, 12);
  } else {
    ctx.fillRect(x + 14, y + 16, 6, 12);
  }
}

// Chim nhỏ bay trang trí trên bầu trời
function drawSkyBird(x, y, wing, color) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.8;
  ctx.beginPath();
  if (wing === 0) {
    // Cánh vểnh lên
    ctx.moveTo(x - 8, y + 4);
    ctx.quadraticCurveTo(x - 4, y - 4, x, y);
    ctx.quadraticCurveTo(x + 4, y - 4, x + 8, y + 4);
  } else {
    // Cánh lướt ngang
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

  // Khuyết mặt trăng bằng màu nền đêm
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

// --- CẬP NHẬT LOGIC GAME ---
function update() {
  if (gameOver) return;

  frameCount++;
  if (frameCount % 6 === 0) {
    dino.legStep = dino.legStep === 0 ? 1 : 0;
  }

  // 1. TĂNG ĐỘ KHÓ THEO THỜI GIAN VÀ ĐIỂM SỐ
  // Tốc độ tăng mượt từ 6 lên tối đa 14
  gameSpeed = baseSpeed + Math.min(score / 180, 8);

  // 2. CHUYỂN ĐỔI NGÀY / ĐÊM THEO MỐC ĐIỂM (Cứ 300 điểm đổi chu kỳ 1 lần)
  const cycle = Math.floor(score / 300);
  isNight = (cycle % 2 === 1);

  // Hiệu ứng mượt chuyển màu nền
  if (isNight && nightProgress < 1) nightProgress = Math.min(1, nightProgress + 0.02);
  if (!isNight && nightProgress > 0) nightProgress = Math.max(0, nightProgress - 0.02);

  // 3. Khủng long nhảy & rơi
  dino.vy += dino.gravity;
  dino.y += dino.vy;
  if (dino.y >= GROUND_Y - dino.h) {
    dino.y = GROUND_Y - dino.h;
    dino.vy = 0;
    dino.grounded = true;
  }

  // 4. Mây bay & Đàn chim nền
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

  // 5. Gờ sỏi mặt đất chạy theo tốc độ game
  groundBumps.forEach(g => {
    g.x -= gameSpeed;
    if (g.x < -20) g.x = canvas.width + Math.random() * 30;
  });

  // 6. Sinh chướng ngại vật (khoảng cách ngắn lại khi game nhanh hơn)
  nextObstacleTimer--;
  if (nextObstacleTimer <= 0) {
    spawnObstacle();
    const minSpacing = Math.max(40, 70 - Math.floor(score / 90));
    nextObstacleTimer = minSpacing + Math.floor(Math.random() * 35);
  }

  // 7. Cập nhật chướng ngại vật & kiểm tra va chạm
  for (let i = obstacles.length - 1; i >= 0; i--) {
    let obs = obstacles[i];
    obs.x -= gameSpeed;

    if (obs.type === 'pterodactyl' && frameCount % 10 === 0) {
      obs.wingState = obs.wingState === 0 ? 1 : 0;
    }

    // Hitbox va chạm
    const p = 5;
    if (
      dino.x + p < obs.x + obs.w - p &&
      dino.x + dino.w - p > obs.x + p &&
      dino.y + p < obs.y + obs.h - p &&
      dino.y + dino.h > obs.y + p
    ) {
      gameOver = true;
      playSound('die');
      if (score > highScore) highScore = score;
    }

    // Qua mặt an toàn và cộng điểm
    if (obs.x + obs.w < 0) {
      obstacles.splice(i, 1);
      score += 10;
      if (score > 0 && score % 100 === 0) {
        playSound('milestone');
      }
    }
  }
}

// --- VẼ TOÀN BỘ KHUNG CẢNH ---
function draw() {
  // Bầu trời chuyển dần giữa Ban Ngày (#f8fafc) và Ban Đêm (#0f172a)
  const bgR = Math.round(248 - nightProgress * (248 - 15));
  const bgG = Math.round(250 - nightProgress * (250 - 23));
  const bgB = Math.round(252 - nightProgress * (252 - 42));
  ctx.fillStyle = `rgb(${bgR}, ${bgG}, ${bgB})`;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  touchHint.style.color = isNight ? '#94a3b8' : '#64748b';

  // Màu sắc chủ đạo của các chi tiết theo ngày/đêm
  const primaryColor = isNight ? '#e2e8f0' : '#475569';
  const groundColor = isNight ? '#475569' : '#94a3b8';
  const cactusColor = isNight ? '#22c55e' : '#15803d';
  const birdColor = isNight ? '#f1f5f9' : '#334155';
  const skyBirdColor = isNight ? '#94a3b8' : '#64748b';
  const cloudColor = isNight ? 'rgba(51, 65, 85, 0.7)' : 'rgba(203, 213, 225, 0.8)';

  // 1. Sao hoặc Mặt trời / Mặt trăng
  if (nightProgress > 0.1) {
    // Ngôi sao lấp lánh ban đêm
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

  // 2. Mây và Đàn chim lượn trên bầu trời
  clouds.forEach(c => drawCloud(c.x, c.y, cloudColor));
  skyBirds.forEach(b => drawSkyBird(b.x, b.y, b.wing, skyBirdColor));

  // 3. Mặt đất và sỏi
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

  // 4. Khủng long T-Rex
  drawDino(dino.x, dino.y, primaryColor);

  // 5. Chướng ngại vật
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

  // 6. Bảng điểm và trạng thái Ngày/Đêm
  ctx.fillStyle = primaryColor;
  ctx.font = 'bold 15px "Courier New", monospace';
  ctx.textAlign = 'right';
  const cycleTag = isNight ? '🌙 ĐÊM' : '☀️ NGÀY';
  ctx.fillText(`${cycleTag}  HI ${highScore.toString().padStart(5, '0')}  ${score.toString().padStart(5, '0')}`, canvas.width - 20, 30);

  // 7. Màn hình Game Over
  if (gameOver) {
    ctx.fillStyle = isNight ? 'rgba(15, 23, 42, 0.85)' : 'rgba(255, 255, 255, 0.85)';
    ctx.fillRect(canvas.width / 2 - 170, 65, 340, 105);

    ctx.fillStyle = '#ef4444';
    ctx.font = 'bold 22px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('G A M E   O V E R', canvas.width / 2, 105);

    ctx.fillStyle = isNight ? '#cbd5e1' : '#64748b';
    ctx.font = '13px sans-serif';
    ctx.fillText('Nhấn Space hoặc chạm màn hình để thử lại', canvas.width / 2, 138);
  }
}

function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop);
}

// --- ĐIỀU KHIỂN (DESKTOP & MOBILE) ---
function handleJump() {
  ensureAudio();
  if (gameOver) {
    resetGame();
  } else if (dino.grounded) {
    dino.vy = dino.jumpPower;
    dino.grounded = false;
    playSound('jump');
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
  e.preventDefault();
  handleJump();
}, { passive: false });

container.addEventListener('mousedown', (e) => {
  handleJump();
});

gameLoop();
</script>
</body>
</html>
"""

components.html(dino_full_code, height=310)
