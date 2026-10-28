# FIPU Shop

A small Vue webshop starter with Vite, Tailwind CSS, and server-side rendering.
Requires Node.js ^22.18.0 or >=24.12.0.

```sh
npm install
npm run dev
```

Open http://127.0.0.1:5173. The Node server uses Vite middleware during development.

```sh
npm run build
npm start
```

Production serves `dist/client` assets and renders Vue using `dist/server` on every page request. `npm run preview` starts this same production server. Set `PORT` to change the default 5173 port. The server binds to localhost.

## Structure

- `src/App.vue`: category navigation, storefront, and in-memory demo cart
- `src/components/ShoppingCart.vue`: bottom-pinned cart, visible only while it contains items
- `src/components/ProductCard.vue`: reusable product card with hover motion and an add-to-cart event
- `src/data/products.js`: sample products, prices in cents
- `src/assets/main.css`: Tailwind styles
- `src/app.js`: fresh Vue SSR app per request
- `src/main.js`: browser hydration
- `src/entry-server.js`: Vue HTML rendering
- `server.js`: development and production HTTP server

`npm test` builds both bundles and checks rendering, request isolation, asset serving, and 404 responses.

This is a starter: products are static, the cart resets on reload, and checkout, payments, authentication, and backend API integration are not included.

The electronics catalog contains 12 smartphones, 8 laptops/tablets, and 10 accessories. Product photos are stored locally in `public/products`; original image URLs are recorded in `public/products/SOURCES.md`. Product data and photos come from https://dummyjson.com/docs/products. EUR prices are illustrative demo values, not current offers.
