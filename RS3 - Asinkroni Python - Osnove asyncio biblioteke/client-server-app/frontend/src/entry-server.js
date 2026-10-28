import { renderToString } from 'vue/server-renderer'
import { createApp } from './app.js'

export function render() {
  return renderToString(createApp())
}
