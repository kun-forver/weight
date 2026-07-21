// Generate colorful Twemoji tabbar icons (gray-state = emoji only, active = emoji + translucent rounded bg).
// Matches the dashboard quick-action emojis: home/food/weight/pk/profile.
// Pipeline: render Twemoji SVG at 300 -> crop content -> re-render at EMOJI_PX -> paste on 81x81 canvas.
// Active variant additionally draws a translucent blue rounded-rectangle behind the emoji.
const fs = require('fs')
const path = require('path')
const NM = process.env.WORKSPACE_NODE_MODULES || 'C:/Users/坤先生的信/.qoderworkcn/workspace/mrkacwb66o1ze5tt/node_modules'
const { Resvg } = require(path.join(NM, '@resvg/resvg-js'))
const { PNG } = require(path.join(NM, 'pngjs'))

const TWEMOJI_DIR = 'C:/Users/坤先生的信/.qoderworkcn/workspace/mrkacwb66o1ze5tt/twemoji'
const OUT_DIR = 'F:/weight/uni-app/src/static/tabbar'
const SIZE = 81       // final canvas
const EMOJI_PX = 55   // emoji content size
const BG = 73         // active background rounded-rect size
const BG_RADIUS = 18
const BG_COLOR = [0, 122, 255, 46] // translucent blue (rgba)

// [out-name, twemoji-codepoint]
const ICONS = [
  ['home', '1f3e0'],
  ['food', '1f34e'],
  ['weight', '2696'],
  ['pk', '2694'],
  ['profile', '1f464'],
]

function renderRaw(svg, width) {
  const resvg = new Resvg(svg, { fitTo: { mode: 'width', value: width }, background: 'rgba(0,0,0,0)' })
  const img = resvg.render()
  return { data: img.pixels, width: img.width, height: img.height }
}

function contentBBox(img) {
  let minX = img.width, minY = img.height, maxX = -1, maxY = -1
  const { data, width, height } = img
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    if (data[(y * width + x) * 4 + 3] > 8) {
      if (x < minX) minX = x; if (x > maxX) maxX = x
      if (y < minY) minY = y; if (y > maxY) maxY = y
    }
  }
  return maxX < 0 ? null : { x: minX, y: minY, w: maxX - minX + 1, h: maxY - minY + 1 }
}

// Render emoji, crop content, return EMOJI_PX-sized RGBA {data,width,height}
function emojiSprite(svgPath) {
  const svg = fs.readFileSync(svgPath, 'utf-8')
  const probe = renderRaw(svg, 300)
  const bb1 = contentBBox(probe)
  if (!bb1) throw new Error('empty: ' + svgPath)
  const renderW = Math.max(1, Math.round(300 * (EMOJI_PX / Math.max(bb1.w, bb1.h))))
  const img = renderRaw(svg, renderW)
  const bb = contentBBox(img)
  if (!bb) throw new Error('empty2: ' + svgPath)
  // crop to content
  const crop = new PNG({ width: bb.w, height: bb.h })
  for (let y = 0; y < bb.h; y++) for (let x = 0; x < bb.w; x++) {
    const src = ((bb.y + y) * img.width + (bb.x + x)) * 4
    const dst = (y * bb.w + x) * 4
    crop.data[dst] = img.data[src]; crop.data[dst + 1] = img.data[src + 1]
    crop.data[dst + 2] = img.data[src + 2]; crop.data[dst + 3] = img.data[src + 3]
  }
  return crop
}

function insideRoundedRect(x, y, x0, y0, x1, y1, r) {
  if (x < x0 || x > x1 || y < y0 || y > y1) return false
  // check the 4 corner circles
  const cx = x < x0 + r ? x0 + r : (x > x1 - r ? x1 - r : x)
  const cy = y < y0 + r ? y0 + r : (y > y1 - r ? y1 - r : y)
  const dx = x - cx, dy = y - cy
  return dx * dx + dy * dy <= r * r || (cx === x || cy === y)
}

function compose(emoji, active) {
  const out = new PNG({ width: SIZE, height: SIZE })
  // 1. active background rounded rect
  if (active) {
    const pad = Math.floor((SIZE - BG) / 2)
    for (let y = 0; y < SIZE; y++) for (let x = 0; x < SIZE; x++) {
      if (insideRoundedRect(x, y, pad, pad, pad + BG - 1, pad + BG - 1, BG_RADIUS)) {
        const dst = (y * SIZE + x) * 4
        out.data[dst] = BG_COLOR[0]; out.data[dst + 1] = BG_COLOR[1]
        out.data[dst + 2] = BG_COLOR[2]; out.data[dst + 3] = BG_COLOR[3]
      }
    }
  }
  // 2. paste emoji centered (alpha over)
  const ox = Math.floor((SIZE - emoji.width) / 2)
  const oy = Math.floor((SIZE - emoji.height) / 2)
  for (let y = 0; y < emoji.height; y++) for (let x = 0; x < emoji.width; x++) {
    const src = (y * emoji.width + x) * 4
    const a = emoji.data[src + 3] / 255
    if (a <= 0) continue
    const dst = ((oy + y) * SIZE + (ox + x)) * 4
    const dstA = out.data[dst + 3] / 255
    const outA = a + dstA * (1 - a)
    for (let c = 0; c < 3; c++) {
      out.data[dst + c] = Math.round((emoji.data[src + c] * a + out.data[dst + c] * dstA * (1 - a)) / outA)
    }
    out.data[dst + 3] = Math.round(outA * 255)
  }
  return PNG.sync.write(out)
}

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true })
for (const [name, cp] of ICONS) {
  const emoji = emojiSprite(path.join(TWEMOJI_DIR, cp + '.svg'))
  fs.writeFileSync(path.join(OUT_DIR, `${name}.png`), compose(emoji, false))
  fs.writeFileSync(path.join(OUT_DIR, `${name}-active.png`), compose(emoji, true))
  console.log(`  ${name}.png + ${name}-active.png (emoji ${emoji.width}x${emoji.height})`)
}
console.log('done')
