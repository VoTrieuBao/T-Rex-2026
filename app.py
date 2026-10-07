import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="T-Rex Runner",
    page_icon="🦖",
    layout="centered"
)

st.title("🦖 T-Rex Runner Game")
st.caption("Nhấn **Phím cách (Space)** hoặc **Mũi tên lên** để nhảy.")

dino_game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f7f7f7;
    font-family: monospace;
  }
  canvas {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  }
</style>
</head>
<body>
<canvas id="gameCanvas" width="600" height="200"></canvas>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let score = 0;
let gameOver = false;

const dino = {
  x: 50,
  y: 150,
  w: 24,
  h: 30,
  vy: 0,
  gravity: 1.2,
  jumpPower: -15,
  isGrounded: true
};

let obstacles = [];
let spawnTimer = 0;

function spawnObstacle() {
  obstacles.push({
    x: canvas.width,
    y: 155,
    w: 16,
    h: 25,
    speed: 5
  });
}

function update() {
  if (gameOver) return;

  dino.vy += dino.gravity;
  dino.y += dino.vy;

  if (dino.y >= 150) {
    dino.y = 150;
    dino.vy = 0;
    dino.isGrounded = true;
  }

  spawnTimer++;
  if (spawnTimer > 85 + Math.random() * 40) {
    spawnObstacle();
    spawnTimer = 0;
  }

  for (let i = obstacles.length - 1; i >= 0; i--) {
    let obs = obstacles[i];
    obs.x -= obs.speed;

    if (
      dino.x < obs.x + obs.w &&
      dino.x + dino.w > obs.x &&
      dino.y < obs.y + obs.h &&
      dino.y + dino.h > obs.y
    ) {
      gameOver = true;
    }

    if (obs.x + obs.w < 0) {
      obstacles.splice(i, 1);
      score += 10;
    }
  }
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = "#777";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, 180);
  ctx.lineTo(canvas.width, 180);
  ctx.stroke();

  ctx.fillStyle = "#333";
  ctx.fillRect(dino.x, dino.y, dino.w, dino.h);

  ctx.fillStyle = "#2e7d32";
  obstacles.forEach(obs => {
    ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
  });

  ctx.fillStyle = "#222";
  ctx.font = "16px monospace";
  ctx.fillText("Điểm: " + score, 480, 25);

  if (gameOver) {
    ctx.fillStyle = "#d32f2f";
    ctx.font = "20px monospace";
    ctx.fillText("GAME OVER!", 230, 90);
    ctx.font = "14px monospace";
    ctx.fillText("Nhấn Space để chơi lại", 205, 120);
  }
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

window.addEventListener('keydown', (e) => {
  if (e.code === 'Space' || e.code === 'ArrowUp') {
    e.preventDefault();
    if (gameOver) {
      gameOver = false;
      score = 0;
      obstacles = [];
      dino.y = 150;
      dino.vy = 0;
    } else if (dino.isGrounded) {
      dino.vy = dino.jumpPower;
      dino.isGrounded = false;
    }
  }
});

loop();
</script>
</body>
</html>
"""

components.html(dino_game_html, height=230)
