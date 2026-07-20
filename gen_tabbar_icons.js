// Render 5 Ant Design SVG icons to PNG (gray + blue states).
const fs = require('fs')
const path = require('path')
const { Resvg } = require('@resvg/resvg-js')

const ICONS_DIR = 'C:/Users/坤先生~1/AppData/Local/Temp/ant-icons/package/inline-svg/outlined'
const OUT_DIR = 'F:/weight/uni-app/src/static/tabbar'
const SIZE = 81

// (name, svg-file, hex-color)
const ICONS = [
  ['home', 'home.svg', '#86868b', '#007aff'],
  ['food', 'apple.svg', '#86868b', '#007aff'],
  ['weight', 'line-chart.svg', '#86868b', '#007aff'],
  ['pk', 'trophy.svg', '#86868b', '#007aff'],
  ['profile', 'user.svg', '#86868b', '#007aff'],
]

function render(svgFile, color, outPath) {
  let svg = fs.readFileSync(path.join(ICONS_DIR, svgFile), 'utf-8')
  // resvg needs xmlns + we inject fill color on the <svg> element
  svg = svg.replace('<svg ', `<svg xmlns="http://www.w3.org/2000/svg" fill="${color}" `)
  const resvg = new Resvg(svg, {
    fitTo: { mode: 'width', value: SIZE },
    background: 'rgba(0,0,0,0)',
  })
  const png = resvg.render().asPng()
  fs.writeFileSync(outPath, png)
}

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true })

for (const [name, file, gray, blue] of ICONS) {
  // Render two states: gray (normal) and blue (active)
  // First wipe old files
  for (const suffix of ['', '-active']) {
    const p = path.join(OUT_DIR, `${name}${suffix}.png`)
    if (fs.existsSync(p)) fs.unlinkSync(p)
  }
  render(file, gray, path.join(OUT_DIR, `${name}.png`))
  render(file, blue, path.join(OUT_DIR, `${name}-active.png`))
  console.log(`  wrote ${name}.png (gray) + ${name}-active.png (blue)`)
}
console.log('done')
