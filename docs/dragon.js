import { measureNaturalWidth, prepare } from './vendor/pretext-1.0.0.js';

const plate = document.querySelector('.plate');
const canvas = plate.querySelector('canvas');
const ctx = canvas.getContext('2d');
const hint = plate.querySelector('.instruction');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const touch = matchMedia('(pointer: coarse)');
const trailFont = '11px monospace';
const glyphs = Array.from('D R A G O N').map(text => ({
  text,
  width: measureNaturalWidth(prepare(text === ' ' ? '·' : text, trailFont))
}));

let joints = [];
let target = { x: 0, y: 0 };
let frame = 0;
let releaseTimer;
let unit = 1;
const step = 6;
const cream = '#fff2cf';
const red = '#ff634b';

function sizeCanvas() {
  const pixelRatio = Math.min(devicePixelRatio, 2);
  canvas.width = Math.round(plate.clientWidth * pixelRatio);
  canvas.height = Math.round(plate.clientHeight * pixelRatio);
  ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  unit = Math.min(1.15, Math.max(.72, plate.clientWidth / 850));
}

function stroke(points, color, width = 1) {
  ctx.beginPath();
  points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.stroke();
}

function drawDragon(time) {
  joints[0] = { ...target };
  // Constrain each vertebra to the preceding one; turns propagate down the tail.
  for (let i = 1; i < joints.length; i++) {
    const last = joints[i - 1];
    const joint = joints[i];
    const angle = Math.atan2(joint.y - last.y, joint.x - last.x);
    joint.x = last.x + Math.cos(angle) * step * unit;
    joint.y = last.y + Math.sin(angle) * step * unit;
  }
  ctx.clearRect(0, 0, plate.clientWidth, plate.clientHeight);
  for (let i = joints.length - 2; i >= 0; i--) {
    const joint = joints[i];
    const next = joints[i + 1];
    const angle = Math.atan2(joint.y - next.y, joint.x - next.x);
    ctx.save();
    ctx.translate(joint.x, joint.y);
    ctx.rotate(angle);
    ctx.scale(unit, unit);
    if (i === 0) {
      // Twin swept horns, jaw, ember eyes and long whiskers.
      for (const side of [-1, 1]) {
        stroke([[-3,side*5],[-12,side*15],[-18,side*16],[-16,side*12]],cream,1.6);
        stroke([[5,side*3],[10,side*9],[17,side*12],[24,side*10]],red,1);
      }
      ctx.beginPath();
      [[-9,-5],[-4,-9],[2,-6],[4,-3],[11,-2],[12,2],[4,4],[1,7],[-7,8],[-11,2]].forEach(([x,y],n)=>n?ctx.lineTo(x,y):ctx.moveTo(x,y));
      ctx.closePath(); ctx.fillStyle='#241a16';ctx.fill();ctx.strokeStyle=cream;ctx.lineWidth=1.7;ctx.stroke();
      for (const side of [-1, 1]) stroke([[-3,side*5],[1,side*4]],red,2.5);
    } else {
      const radius = 1 + 5.5 * (1 - i / joints.length);
      stroke([[0,0],[-step,0]],'#32231f',radius*2+2);
      for (const side of [-1, 1]) {
        stroke([[1,side*radius],[-step,side*radius*.9]],cream,1.2);
        if (i < 18 && i % 2 === 0) stroke([[1,side*radius],[-5,side*(radius+4)]],red,1.6);
        if (i === 4 || i === 12) {
          const flick = 2*Math.sin(time/220+i);
          stroke([[0,side*3],[3,side*12],[-4,side*(17+flick)],[-1,side*21]],cream,1.8);
          stroke([[-4,side*(17+flick)],[-7,side*21]],cream,1);
        }
      }
      stroke([[1,-radius],[-3,radius]],'#e2a18a',.9);
    }
    ctx.restore();
  }
  // Pretext measures the lettering once; each measured advance sets its place along the tail tangent.
  const tip = joints.at(-1), near = joints.at(-2);
  const tailAngle = Math.atan2(tip.y-near.y,tip.x-near.x);
  ctx.save();
  ctx.translate(tip.x,tip.y);
  ctx.scale(unit,unit);
  ctx.font=trailFont;
  let advance=5;
  const lettering = Math.cos(tailAngle) < 0 ? glyphs.toReversed() : glyphs;
  lettering.forEach(({text,width},i)=>{
    ctx.fillStyle='rgba(255,210,170,'+(1-i*.05)+')';
    ctx.fillText(text,Math.cos(tailAngle)*advance-width/2,Math.sin(tailAngle)*advance+3);
    advance+=width+1;
  });
  ctx.restore();
  frame=requestAnimationFrame(drawDragon);
}

function stop() {
  clearTimeout(releaseTimer);
  cancelAnimationFrame(frame);
  frame=0;
  joints=[];
  plate.classList.remove('summoned');
  ctx.clearRect(0,0,plate.clientWidth,plate.clientHeight);
}
function summon(event) {
  if (motion.matches) return;
  clearTimeout(releaseTimer);
  const bounds=canvas.getBoundingClientRect();
  target={x:event.clientX-bounds.left,y:event.clientY-bounds.top};
  if (frame) return;
  joints=Array.from({length:25},(_,i)=>({x:target.x-i*step*unit,y:target.y+Math.sin(i/6)*5*unit}));
  plate.classList.add('summoned');
  frame=requestAnimationFrame(drawDragon);
}
function updateHint() {
  stop();
  hint.textContent=motion.matches?'Dragon Index':touch.matches?'Touch to summon the dragon':'Move to summon the dragon';
}
new ResizeObserver(sizeCanvas).observe(plate);
plate.addEventListener('pointerdown',summon);
plate.addEventListener('pointermove',summon);
plate.addEventListener('pointerleave',event=>{
  if (event.pointerType !== 'touch') stop();
});
plate.addEventListener('pointercancel',stop);
plate.addEventListener('pointerup',event=>{
  if(event.pointerType==='touch') releaseTimer=setTimeout(stop,900);
});
window.addEventListener('blur',stop);
motion.addEventListener('change',updateHint);
touch.addEventListener('change',updateHint);
sizeCanvas();
updateHint();
