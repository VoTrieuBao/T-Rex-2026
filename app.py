import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="T-Rex Runner Pro",
    page_icon="🦖",
    layout="wide"
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🦖 Chrome Dino T-Rex Runner")
st.caption("💻 **Máy tính**: Nhấn `Space` hoặc `Phím mũi tên lên` | 📱 **Điện thoại**: Chạm vào màn hình để nhảy")

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
    padding: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  #container {
    width: 100%;
    max-width: 780px;
    position: relative;
    background: #fdfdfd;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    overflow: hidden;
    touch-action: manipulation;
  }
  canvas {
    display: block;
    width: 100%;
    height: auto;
    background: #fbfbfb;
  }
  #touchHint {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
    color: #94a3b8;
    pointer-events: none;
  }
</style>
</head>
<body>

<div id="container">
  <canvas id="gameCanvas" width="800" height="260"></canvas>
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
      osc.frequency.setValueAtTime(260, now);
      osc.frequency.exponentialRampToValueAtTime(70, now + 0.28);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
      osc.start(now);
      osc.stop(now + 0.28);
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

// --- BIẾN VÀ CẤU HÌNH GAME ---
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const GROUND_Y = 215;
let gameSpeed = 6;
let score = 0;
let highScore = 0;
let gameOver = false;
let frameCount = 0;

// Khủng long
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

// Phong cảnh: Mây & Đất sỏi
let clouds = [
  { x: 200, y: 50, speed: 0.8 },
  { x: 550, y: 80, speed: 0.6 },
  { x: 750, y: 40, speed: 0.7 }
];

let groundBumps = [];
for (let i = 0; i < 800; i += 30) {
  groundBumps.push({ x: i, len: 10 + Math.random() * 15 });
}

// Chướng ngại vật
let obstacles = [];
let nextObstacleTimer = 70;

function resetGame() {
  dino.y = GROUND_Y - 44;
  dino.vy = 0;
  dino.grounded = true;
  obstacles = [];
  gameSpeed = 6;
  score = 0;
  frameCount = 0;
  nextObstacleTimer = 60;
  gameOver = false;
}

function spawnObstacle() {
  const typeRand = Math.random();
  // Điểm > 200 mới bắt đầu xuất hiện chim bay
  if (score > 200 && typeRand < 0.35) {
    // Chim Pterodactyl: bay thấp hoặc bay vừa
    const birdY = Math.random() < 0.5 ? GROUND_Y - 55 : GROUND_Y - 32;
    obstacles.push({
      type: 'bird',
      x: canvas.width + 20,
      y: birdY,
      w: 40,
      h: 28,
      wingState: 0
    });
  } else if (typeRand < 0.65) {
    // Cụm xương rồng đôi/ba
    obstacles.push({
      type: 'cactus_group',
      x: canvas.width + 20,
      y: GROUND_Y - 45,
      w: 38,
      h: 45
    });
  } else {
    // Xương rồng đơn lẻ
    obstacles.push({
      type: 'cactus_single',
      x: canvas.width + 20,
      y: GROUND_Y - 40,
      w: 22,
      h: 40
    });
  }
}

// --- HÀM VẼ SPRITE BẰNG CANVAS PIXEL ---
function drawDino(x, y) {
  ctx.fillStyle = '#475569';

  // Thân & đầu
  ctx.fillRect(x + 16, y + 2, 22, 14); // Đầu
  ctx.fillRect(x + 12, y + 14, 20, 18); // Thân
  ctx.fillRect(x + 4, y + 18, 10, 10); // Đuôi

  // Mắt khủng long
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(x + 30, y + 5, 4, 4);

  // Tay nhỏ
  ctx.fillStyle = '#475569';
  ctx.fillRect(x + 32, y + 20, 6, 3);

  // Chân khủng long chạy luân phiên
  if (!dino.grounded) {
    // Đang nhảy co chân
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

function drawCactus(x, y, w, h) {
  ctx.fillStyle = '#166534';
  // Thân chính
  ctx.fillRect(x + w * 0.35, y, w * 0.3, h);
  // Nhánh trái
  ctx.fillRect(x, y + h * 0.3, w * 0.35, h * 0.15);
  ctx.fillRect(x, y + h * 0.15, w * 0.15, h * 0.2);
  // Nhánh phải
  ctx.fillRect(x + w * 0.65, y + h * 0.4, w * 0.35, h * 0.15);
  ctx.fillRect(x + w * 0.85, y + h * 0.25, w * 0.15, h * 0.2);
}

function drawBird(x, y, w, h, wing) {
  ctx.fillStyle = '#334155';
  // Thân & mỏ chim
  ctx.fillRect(x + 8, y + 10, 22, 10);
  ctx.fillRect(x, y + 12, 8, 4); // Mỏ
  ctx.fillRect(x + 28, y + 12, 10, 6); // Đuôi

  // Cánh chim vỗ lên / cụp xuống
  if (wing === 0) {
    ctx.fillRect(x + 14, y, 6, 12); // Cánh giương lên
  } else {
    ctx.fillRect(x + 14, y + 16, 6, 12); // Cánh cụp xuống
  }
}

function drawCloud(x, y) {
  ctx.fillStyle = '#cbd5e1';
  ctx.beginPath();
  ctx.arc(x, y, 14, 0, Math.PI * 2);
  ctx.arc(x + 14, y - 6, 16, 0, Math.PI * 2);
  ctx.arc(x + 30, y, 12, 0, Math.PI * 2);
  ctx.fill();
}

// --- VÒNG LẶP CHÍNH CỦA GAME ---
function update() {
  if (gameOver) return;

  frameCount++;
  if (frameCount % 6 === 0) {
    dino.legStep = dino.legStep === 0 ? 1 : 0;
  }

  // Tăng tốc dần theo điểm số
  gameSpeed = 6 + Math.min(score / 250, 7);

  // Nhảy & trọng lực
  dino.vy += dino.gravity;
  dino.y += dino.vy;
  if (dino.y >= GROUND_Y - dino.h) {
    dino.y = GROUND_Y - dino.h;
    dino.vy = 0;
    dino.grounded = true;
  }

  // Cập nhật mây
  clouds.forEach(c => {
    c.x -= c.speed;
    if (c.x < -60) {
      c.x = canvas.width + 30;
      c.y = 30 + Math.random() * 70;
    }
  });

  // Cập nhật gờ đất sỏi
  groundBumps.forEach(g => {
    g.x -= gameSpeed;
    if (g.x < -20) g.x = canvas.width + Math.random() * 30;
  });

  // Sinh chướng ngại vật
  nextObstacleTimer--;
  if (nextObstacleTimer <= 0) {
    spawnObstacle();
    // Khoảng cách ngẫu nhiên an toàn giữa các vật cản
    nextObstacleTimer = Math.floor(65 + Math.random() * 50 - Math.min(score / 50, 20));
  }

  // Cập nhật chướng ngại vật & kiểm tra va chạm
  for (let i = obstacles.length - 1; i >= 0; i--) {
    let obs = obstacles[i];
    obs.x -= gameSpeed;

    if (obs.type === 'bird' && frameCount % 12 === 0) {
      obs.wingState = obs.wingState === 0 ? 1 : 0;
    }

    // Hitbox va chạm (thu hẹp 4px viền để hitbox tự nhiên, công bằng hơn)
    const padding = 5;
    if (
      dino.x + padding < obs.x + obs.w - padding &&
      dino.x + dino.w - padding > obs.x + padding &&
      dino.y + padding < obs.y + obs.h - padding &&
      dino.y + dino.h > obs.y + padding
    ) {
      gameOver = true;
      playSound('die');
      if (score > highScore) highScore = score;
    }

    // Xóa vật cản ra ngoài màn hình và tính điểm
    if (obs.x + obs.w < 0) {
      obstacles.splice(i, 1);
      score += 10;
      if (score > 0 && score % 100 === 0) {
        playSound('milestone');
      }
    }
  }
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 1. Mây trời
  clouds.forEach(c => drawCloud(c.x, c.y));

  // 2. Mặt đất
  ctx.strokeStyle = '#94a3b8';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, GROUND_Y);
  ctx.lineTo(canvas.width, GROUND_Y);
  ctx.stroke();

  // Đốm sỏi trên đường
  ctx.strokeStyle = '#cbd5e1';
  ctx.lineWidth = 1.5;
  groundBumps.forEach(g => {
    ctx.beginPath();
    ctx.moveTo(g.x, GROUND_Y + 5);
    ctx.lineTo(g.x + g.len, GROUND_Y + 5);
    ctx.stroke();
  });

  // 3. Khủng long
  drawDino(dino.x, dino.y);

  // 4. Chướng ngại vật
  obstacles.forEach(obs => {
    if (obs.type === 'bird') {
      drawBird(obs.x, obs.y, obs.w, obs.h, obs.wingState);
    } else if (obs.type === 'cactus_group') {
      drawCactus(obs.x, obs.y, obs.w * 0.5, obs.h);
      drawCactus(obs.x + obs.w * 0.5, obs.y + 6, obs.w * 0.45, obs.h - 6);
    } else {
      drawCactus(obs.x, obs.y, obs.w, obs.h);
    }
  });

  // 5. Bảng điểm
  ctx.fillStyle = '#475569';
  ctx.font = 'bold 15px "Courier New", monospace';
  ctx.textAlign = 'right';
  ctx.fillText(`HI ${highScore.toString().padStart(5, '0')}  ${score.toString().padStart(5, '0')}`, canvas.width - 20, 30);

  // 6. Giao diện Game Over
  if (gameOver) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
    ctx.fillRect(canvas.width / 2 - 160, 60, 320, 100);

    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 22px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('G A M E   O V E R', canvas.width / 2, 100);

    ctx.fillStyle = '#64748b';
    ctx.font = '13px sans-serif';
    ctx.fillText('Nhấn Space hoặc chạm màn hình để thử lại', canvas.width / 2, 132);
  }
}

function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop);
}

// --- SỰ KIỆN ĐIỀU KHIỂN (MÁY TÍNH & ĐIỆN THOẠI) ---
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

// Điều khiển phím trên laptop/PC
window.addEventListener('keydown', (e) => {
  if (e.code === 'Space' || e.code === 'ArrowUp') {
    e.preventDefault();
    handleJump();
  }
});

// Điều khiển chạm cảm ứng trên điện thoại
const container = document.getElementById('container');
container.addEventListener('touchstart', (e) => {
  e.preventDefault();
  handleJump();
}, { passive: false });

container.addEventListener('mousedown', (e) => {
  handleJump();
});

// Bắt đầu game
gameLoop();
</script>
</body>
</html>
"""

components.html(dino_full_code, height=300)
