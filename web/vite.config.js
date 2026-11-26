import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// The site is a GitHub Pages project site, so it lives under /yoto-playlist/.
export default defineConfig({
  base: '/yoto-playlist/',
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/apple-touch-icon.png'],
      manifest: {
        name: 'Yoto shelf',
        short_name: 'Yoto',
        description: 'Fifty Yoto cards, ranked for a two-year-old.',
        start_url: '/yoto-playlist/#/',
        scope: '/yoto-playlist/',
        display: 'standalone',
        background_color: '#FBF6E8',
        theme_color: '#FBF6E8',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icons/maskable-192.png', sizes: '192x192', type: 'image/png', purpose: 'maskable' },
          { src: 'icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
        ]
      },
      workbox: {
        // Shell + the 50 grid thumbnails are precached; full covers are fetched
        // when a card is opened and kept after that.
        globPatterns: ['**/*.{js,css,html,json,png,svg}', 'covers/*.jpg'],
        maximumFileSizeToCacheInBytes: 4 * 1024 * 1024,
        runtimeCaching: [
          {
            urlPattern: /\/covers\/full\/.*\.jpg$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'full-covers',
              expiration: { maxEntries: 80, maxAgeSeconds: 60 * 60 * 24 * 365 }
            }
          },
          {
            urlPattern: /covers-sheet\.jpg$/,
            handler: 'CacheFirst',
            options: { cacheName: 'sheet' }
          }
        ]
      }
    })
  ]
})
