import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

// uni-app 3.x (Vue 3 + Vite) build config.
// The `uni` CLI sets UNI_PLATFORM env var (mp-weixin / h5) and invokes vite;
// this file is what actually loads the uni plugin that drives compilation.
export default defineConfig({
  plugins: [uni()],
})
