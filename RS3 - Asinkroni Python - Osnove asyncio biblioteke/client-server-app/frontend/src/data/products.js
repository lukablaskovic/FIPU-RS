// shortcut: static demo catalog and illustrative EUR prices, replace with a live catalog before selling.
export const products = [
  {
    "id": 121,
    "name": "iPhone 5s",
    "category": "Smartphones",
    "price": 19999,
    "image": "/products/121.webp"
  },
  {
    "id": 122,
    "name": "iPhone 6",
    "category": "Smartphones",
    "price": 29999,
    "image": "/products/122.webp"
  },
  {
    "id": 123,
    "name": "iPhone 13 Pro",
    "category": "Smartphones",
    "price": 109999,
    "image": "/products/123.webp"
  },
  {
    "id": 124,
    "name": "iPhone X",
    "category": "Smartphones",
    "price": 89999,
    "image": "/products/124.webp"
  },
  {
    "id": 125,
    "name": "Oppo A57",
    "category": "Smartphones",
    "price": 24999,
    "image": "/products/125.webp"
  },
  {
    "id": 126,
    "name": "Oppo F19 Pro Plus",
    "category": "Smartphones",
    "price": 39999,
    "image": "/products/126.webp"
  },
  {
    "id": 127,
    "name": "Oppo K1",
    "category": "Smartphones",
    "price": 29999,
    "image": "/products/127.webp"
  },
  {
    "id": 128,
    "name": "Realme C35",
    "category": "Smartphones",
    "price": 14999,
    "image": "/products/128.webp"
  },
  {
    "id": 129,
    "name": "Realme X",
    "category": "Smartphones",
    "price": 29999,
    "image": "/products/129.webp"
  },
  {
    "id": 130,
    "name": "Realme XT",
    "category": "Smartphones",
    "price": 34999,
    "image": "/products/130.webp"
  },
  {
    "id": 131,
    "name": "Samsung Galaxy S7",
    "category": "Smartphones",
    "price": 29999,
    "image": "/products/131.webp"
  },
  {
    "id": 132,
    "name": "Samsung Galaxy S8",
    "category": "Smartphones",
    "price": 49999,
    "image": "/products/132.webp"
  },
  {
    "id": 78,
    "name": "Apple MacBook Pro 14 Inch Space Grey",
    "category": "Laptops & tablets",
    "price": 199999,
    "image": "/products/78.webp"
  },
  {
    "id": 79,
    "name": "Asus Zenbook Pro Dual Screen Laptop",
    "category": "Laptops & tablets",
    "price": 179999,
    "image": "/products/79.webp"
  },
  {
    "id": 80,
    "name": "Huawei Matebook X Pro",
    "category": "Laptops & tablets",
    "price": 139999,
    "image": "/products/80.webp"
  },
  {
    "id": 81,
    "name": "Lenovo Yoga 920",
    "category": "Laptops & tablets",
    "price": 109999,
    "image": "/products/81.webp"
  },
  {
    "id": 82,
    "name": "New DELL XPS 13 9300 Laptop",
    "category": "Laptops & tablets",
    "price": 149999,
    "image": "/products/82.webp"
  },
  {
    "id": 159,
    "name": "iPad Mini 2021 Starlight",
    "category": "Laptops & tablets",
    "price": 49999,
    "image": "/products/159.webp"
  },
  {
    "id": 160,
    "name": "Samsung Galaxy Tab S8 Plus Grey",
    "category": "Laptops & tablets",
    "price": 59999,
    "image": "/products/160.webp"
  },
  {
    "id": 161,
    "name": "Samsung Galaxy Tab White",
    "category": "Laptops & tablets",
    "price": 34999,
    "image": "/products/161.webp"
  },
  {
    "id": 99,
    "name": "Amazon Echo Plus",
    "category": "Accessories",
    "price": 9999,
    "image": "/products/99.webp"
  },
  {
    "id": 100,
    "name": "Apple Airpods",
    "category": "Accessories",
    "price": 12999,
    "image": "/products/100.webp"
  },
  {
    "id": 101,
    "name": "Apple AirPods Max Silver",
    "category": "Accessories",
    "price": 54999,
    "image": "/products/101.webp"
  },
  {
    "id": 102,
    "name": "Apple Airpower Wireless Charger",
    "category": "Accessories",
    "price": 7999,
    "image": "/products/102.webp"
  },
  {
    "id": 103,
    "name": "Apple HomePod Mini Cosmic Grey",
    "category": "Accessories",
    "price": 9999,
    "image": "/products/103.webp"
  },
  {
    "id": 104,
    "name": "Apple iPhone Charger",
    "category": "Accessories",
    "price": 1999,
    "image": "/products/104.webp"
  },
  {
    "id": 105,
    "name": "Apple MagSafe Battery Pack",
    "category": "Accessories",
    "price": 9999,
    "image": "/products/105.webp"
  },
  {
    "id": 106,
    "name": "Apple Watch Series 4 Gold",
    "category": "Accessories",
    "price": 34999,
    "image": "/products/106.webp"
  },
  {
    "id": 107,
    "name": "Beats Flex Wireless Earphones",
    "category": "Accessories",
    "price": 4999,
    "image": "/products/107.webp"
  },
  {
    "id": 110,
    "name": "Selfie Lamp with iPhone",
    "category": "Accessories",
    "price": 1499,
    "image": "/products/110.webp"
  }
]

export const formatPrice = (cents) => `€${(cents / 100).toFixed(2)}`
