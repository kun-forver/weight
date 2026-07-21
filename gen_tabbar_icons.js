// Render 5 Ant Design SVG icons to PNG (gray + blue states) with UNIFORM padding.
// Strategy: render at 1024 -> find content bbox -> re-render at scale where
// content fits in CONTENT_PX -> paste centered on SIZE x SIZE transparent canvas.
// This guarantees gray and active variants are identical in size/position.
const fs = require('fs')
const path = require('path')
const { Resvg } = require(path.join(process.env.WORKSPACE_NODE_MODULES || 'C:/Users/坤先生的信/.qoderworkcn/workspace/mrkacwb66o1ze5tt/node_modules', '@resvg/resvg-js'))
const { PNG } = require(path.join(process.env.WORKSPACE_NODE_MODULES || 'C:/Users/坤先生的信/.qoderworkcn/workspace/mrkacwb66o1ze5tt/node_modules', 'pngjs'))

const ICONS_DIR = 'C:/Users/坤先生~1/AppData/Local/Temp/ant-icons/package/inline-svg/outlined'
const OUT_DIR = 'F:/weight/uni-app/src/static/tabbar'
const SIZE = 81        // final canvas (WeChat recommended)
const CONTENT_PX = 57  // icon content size -> ~12px padding each side

const ICONS = [
  ['home', 'home.svg', '#86868b', '#007aff'],
  ['food', 'apple.svg', '#86868b', '#007aff'],
  ['weight', 'line-chart.svg', '#86868b', '#007aff'],
  ['pk', 'trophy.svg', '#86868b', '#007aff'],
  ['profile', 'user.svg', '#86868b', '#007aff'],
]

function prepareSvg(svgFile, color) {
  let svg = fs.readFileSync(path.join(ICONS_DIR, svgFile), 'utf-8')
  // resvg needs xmlns + we inject fill color on the <svg> element
  return svg.replace('<svg ', `<svg xmlns="http://www.w3.org/2000/svg" fill="${color}" `)
}

function renderRaw(svg, width) {
  const resvg = new Resvg(svg, {
    fitTo: { mode: 'width', value: width },
    background: 'rgba(0,0,0,0)',
  })
  const img = resvg.render()
  return { data: img.pixels, width: img.width, height: img.height }
}

// Find bounding box of non-transparent pixels
function contentBBox(img) {
  let minX = img.width, minY = img.height, maxX = -1, maxY = -1
  const { data, width, height } = img
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const a = data[(y * width + x) * 4 + 3]
      if (a > 8) {
        if (x < minX) minX = x
        if (x > maxX) maxX = x
        if (y < minY) minY = y
        if (y > maxY) maxY = y
      }
    }
  }
  if (maxX < 0) return null
  return { x: minX, y: minY, w: maxX - minX + 1, h: maxY - minY + 1 }
}

function renderIcon(svgFile, color) {
  const svg = prepareSvg(svgFile, color)

  // Pass 1: render at 1024 to measure content
  const probe = renderRaw(svg, 1024)
  const bb1 = contentBBox(probe)
  if (!bb1) throw new Error(`empty render: ${svgFile}`)

  // Pass 2: re-render so content lands at ~CONTENT_PX
  const scale = CONTENT_PX / Math.max(bb1.w, bb1.h)
  const renderW = Math.max(1, Math.round(1024 * scale))
  const img = renderRaw(svg, renderW)
  const bb = contentBBox(img)
  if (!bb) throw new Error(`empty render(2): ${svgFile}`)

  // Paste content centered on SIZE x SIZE transparent canvas
  const out = new PNG({ width: SIZE, height: SIZE })
  const offX = Math.round((SIZE - bb.w) / 2)
  const offY = Math.round((SIZE - bb.h) / 2)
  for (let y = 0; y < bb.h; y++) {
    for (let x = 0; x < bb.w; x++) {
      const src = ((bb.y + y) * img.width + (bb.x + x)) * 4
      const dst = ((offY + y) * SIZE + (offX + x)) * 4
      out.data[dst] = img.data[src]
      out.data[dst + 1] = img.data[src + 1]
      out.data[dst + 2] = img.data[src + 2]
      out.data[dst + 3] = img.data[src + 3]
    }
  }
  return PNG.sync.write(out)
}

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true })

for (const [name, file, gray, blue] of ICONS) {
  fs.writeFileSync(path.join(OUT_DIR, `${name}.png`), renderIcon(file, gray))
  fs.writeFileSync(path.join(OUT_DIR, `${name}-active.png`), renderIcon(file, blue))
  console.log(`  wrote ${name}.png + ${name}-active.png (content ${CONTENT_PX}px in ${SIZE}px canvas)`)
}
console.log('done')
