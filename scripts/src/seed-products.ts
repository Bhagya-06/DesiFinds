import fs from "fs";
import path from "path";

const workspaceRoot = path.resolve(import.meta.dirname, "../..");
const outputPath = path.resolve(workspaceRoot, "data/products.json");

// Ensure data directory exists
fs.mkdirSync(path.dirname(outputPath), { recursive: true });

// ────── Brand definitions ──────
const brands = [
  { name: "Snitch", url: "https://www.snitch.co.in", categories: ["Apparel"] },
  { name: "Rare Rabbit", url: "https://rarerabbit.in", categories: ["Apparel"] },
  { name: "Bombay Shirt Company", url: "https://bombaytshirtcompany.com", categories: ["Apparel"] },
  { name: "Nicobar", url: "https://nicobar.com", categories: ["Apparel", "Home Decor"] },
  { name: "The Souled Store", url: "https://www.thesouledstore.com", categories: ["Apparel"] },
  { name: "House of Pataudi", url: "https://houseofpataudi.com", categories: ["Apparel"] },
  { name: "Minimalist", url: "https://beminimalist.co", categories: ["Skincare"] },
  { name: "Dot & Key", url: "https://www.dotandkey.com", categories: ["Skincare"] },
  { name: "The Derma Co", url: "https://thedermacompany.com", categories: ["Skincare"] },
  { name: "Plum", url: "https://plumgoodness.com", categories: ["Skincare"] },
  { name: "Juicy Chemistry", url: "https://juicychemistry.com", categories: ["Skincare"] },
  { name: "Re'equil", url: "https://reequil.com", categories: ["Skincare"] },
  { name: "boAt", url: "https://www.boat-lifestyle.com", categories: ["Audio", "Electronics"] },
  { name: "Noise", url: "https://www.gonoise.com", categories: ["Electronics", "Watches"] },
  { name: "Boult", url: "https://boult.com", categories: ["Audio"] },
  { name: "Portronics", url: "https://www.portronics.com", categories: ["Electronics"] },
  { name: "Fire-Boltt", url: "https://www.fireboltt.com", categories: ["Watches", "Electronics"] },
  { name: "Pebble", url: "https://pebblesmartwatch.com", categories: ["Watches"] },
  { name: "Titan", url: "https://www.titan.co.in", categories: ["Watches"] },
  { name: "Fastrack", url: "https://www.fastrack.in", categories: ["Watches", "Eyewear"] },
  { name: "Bangalore Watch Company", url: "https://bangalorewatchcompany.com", categories: ["Watches"] },
  { name: "JAIPUR WATCH COMPANY", url: "https://jaipurwatch.com", categories: ["Watches"] },
  { name: "Mokobara", url: "https://www.mokobara.com", categories: ["Bags"] },
  { name: "Zouk", url: "https://www.zouk.co.in", categories: ["Bags"] },
  { name: "DailyObjects", url: "https://www.dailyobjects.com", categories: ["Bags", "Electronics"] },
  { name: "Fur Jaden", url: "https://www.furjaden.com", categories: ["Bags", "Footwear"] },
  { name: "Neeman's", url: "https://www.neemans.com", categories: ["Footwear"] },
  { name: "Comet", url: "https://cometshoes.com", categories: ["Footwear"] },
  { name: "Paaduks", url: "https://paaduks.com", categories: ["Footwear"] },
  { name: "Nappa Dori", url: "https://nappadori.com", categories: ["Bags", "Footwear"] },
  { name: "Chumbak", url: "https://www.chumbak.com", categories: ["Home Decor", "Bags"] },
  { name: "Wakefit", url: "https://www.wakefit.co", categories: ["Furniture"] },
  { name: "Wooden Street", url: "https://www.woodenstreet.com", categories: ["Furniture"] },
  { name: "Pepperfry", url: "https://www.pepperfry.com", categories: ["Furniture"] },
  { name: "Wonderchef", url: "https://www.wonderchef.com", categories: ["Kitchen"] },
  { name: "Borosil", url: "https://www.borosil.com", categories: ["Kitchen"] },
  { name: "Stahl", url: "https://www.stahl.in", categories: ["Kitchen"] },
  { name: "GIVA", url: "https://www.giva.co", categories: ["Jewelry"] },
  { name: "Melorra", url: "https://www.melorra.com", categories: ["Jewelry"] },
  { name: "Bhima Jewellers", url: "https://www.bhima.co.in", categories: ["Jewelry"] },
  { name: "Bella Vita", url: "https://bellavitaorganic.com", categories: ["Perfumes", "Skincare"] },
  { name: "Naso Profumi", url: "https://nasoprofumi.com", categories: ["Perfumes"] },
  { name: "Bombay Perfumery", url: "https://bombayperfumery.com", categories: ["Perfumes"] },
  { name: "Lenskart", url: "https://www.lenskart.com", categories: ["Eyewear"] },
  { name: "Aqualens", url: "https://www.aqualens.in", categories: ["Eyewear"] },
  { name: "Cultsport", url: "https://cultsport.com", categories: ["Fitness"] },
  { name: "Boldfit", url: "https://boldfit.in", categories: ["Fitness"] },
  { name: "Decathlon India", url: "https://www.decathlon.in", categories: ["Fitness"] },
];

// ────── Image pools per category ──────
const imagesByCategory: Record<string, string[]> = {
  Apparel: [
    "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400",
    "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400",
    "https://images.unsplash.com/photo-1581803118522-7b72a50f7e9f?w=400",
    "https://images.unsplash.com/photo-1620799139834-6b8f844fbe61?w=400",
    "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=400",
    "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400",
  ],
  Footwear: [
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
    "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=400",
    "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400",
    "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=400",
    "https://images.unsplash.com/photo-1519415510236-718bdfcd89c8?w=400",
  ],
  Electronics: [
    "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400",
    "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400",
    "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400",
    "https://images.unsplash.com/photo-1588702547923-7408b4aae01c?w=400",
  ],
  Audio: [
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
    "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400",
    "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400",
    "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=400",
  ],
  Watches: [
    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
    "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400",
    "https://images.unsplash.com/photo-1434056886845-dac89ffe9b56?w=400",
    "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400",
  ],
  Skincare: [
    "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400",
    "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400",
    "https://images.unsplash.com/photo-1576426863848-c21f53c60b19?w=400",
    "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400",
  ],
  Bags: [
    "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400",
    "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
    "https://images.unsplash.com/photo-1614179689702-355944cd0918?w=400",
    "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=400",
  ],
  Jewelry: [
    "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400",
    "https://images.unsplash.com/photo-1602173574767-37ac01994b2a?w=400",
    "https://images.unsplash.com/photo-1576021182211-9ea8dced3690?w=400",
    "https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=400",
  ],
  Furniture: [
    "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400",
    "https://images.unsplash.com/photo-1540574163026-643ea20ade25?w=400",
    "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400",
    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
  ],
  "Home Decor": [
    "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=400",
    "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=400",
    "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=400",
    "https://images.unsplash.com/photo-1585412459212-7e3b00a6a333?w=400",
  ],
  Kitchen: [
    "https://images.unsplash.com/photo-1585515320310-259814833e62?w=400",
    "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400",
    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400",
    "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?w=400",
  ],
  Fitness: [
    "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400",
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400",
    "https://images.unsplash.com/photo-1599058917765-a780eda07a3e?w=400",
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400",
  ],
  Perfumes: [
    "https://images.unsplash.com/photo-1541643600914-78b084683702?w=400",
    "https://images.unsplash.com/photo-1595535873420-a599195b3f4a?w=400",
    "https://images.unsplash.com/photo-1588514912908-b6d54f680a0e?w=400",
    "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400",
  ],
  Eyewear: [
    "https://images.unsplash.com/photo-1577803645773-f96470509666?w=400",
    "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400",
    "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400",
    "https://images.unsplash.com/photo-1614683489905-3a10e5b7a3e7?w=400",
  ],
};

// ────── Product templates per category ──────
type ProductTemplate = {
  namePrefix: string;
  nameSuffixes: string[];
  materials: string[];
  tags: string[];
  basePrice: number;
  priceVariance: number;
  baseRating: number;
  reviewSummaryTemplates: string[];
  badges: string[];
  descriptionTemplate: string;
};

const categoryTemplates: Record<string, ProductTemplate[]> = {
  Apparel: [
    {
      namePrefix: "Premium Linen",
      nameSuffixes: ["Shirt", "Kurta", "Overshirt", "Blazer"],
      materials: ["100% Linen", "Organic Cotton Lining"],
      tags: ["linen", "premium", "casual", "summer", "breathable"],
      basePrice: 2499,
      priceVariance: 1500,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Customers love the breathable linen fabric and premium finish. Perfect for Indian summers.",
        "Excellent quality linen. The fabric gets softer with every wash.",
      ],
      badges: ["Premium Quality", "Made in India", "Sustainable"],
      descriptionTemplate:
        "Crafted from premium linen fabric, this piece is designed for the modern Indian wardrobe. Features a relaxed fit with meticulous tailoring.",
    },
    {
      namePrefix: "Classic Oxford",
      nameSuffixes: ["Shirt", "Button-Down", "Formal Shirt"],
      materials: ["100% Egyptian Cotton", "Mother-of-pearl buttons"],
      tags: ["oxford", "cotton", "formal", "office", "classic"],
      basePrice: 1999,
      priceVariance: 1200,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Superb cotton quality. Great for office wear.",
        "The fabric is crisp and holds its shape well through the day.",
      ],
      badges: ["Premium Quality", "Highly Rated"],
      descriptionTemplate:
        "A timeless oxford shirt made from the finest Egyptian cotton. Perfect for boardrooms and brunches alike.",
    },
    {
      namePrefix: "Block Print",
      nameSuffixes: ["Kurta", "Shirt", "Co-ord Set"],
      materials: ["Hand-block printed cotton", "Natural dyes"],
      tags: ["block print", "handcrafted", "ethnic", "indian print", "artisan"],
      basePrice: 1799,
      priceVariance: 800,
      baseRating: 4.6,
      reviewSummaryTemplates: [
        "Beautiful hand-block prints. Very authentic Indian craftsmanship.",
        "Love the traditional motifs on premium cotton. Great gift option.",
      ],
      badges: ["Handcrafted", "Artisan Made", "Made in India"],
      descriptionTemplate:
        "Hand-block printed using traditional Rajasthani techniques. Each piece is unique, celebrating India's rich textile heritage.",
    },
    {
      namePrefix: "Slim Fit Chinos",
      nameSuffixes: ["Trousers", "Pants", "Bottoms"],
      materials: ["98% Cotton, 2% Stretch", "Metal button"],
      tags: ["chinos", "slim fit", "casual", "versatile", "everyday"],
      basePrice: 1499,
      priceVariance: 600,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Great fit and comfortable fabric. Very versatile.",
        "Perfect slim fit, excellent quality for the price.",
      ],
      badges: ["Better Value", "Highly Rated"],
      descriptionTemplate: "Slim-fit chinos with a comfortable stretch. Pairs well with everything from kurtas to shirts.",
    },
    {
      namePrefix: "Oversized",
      nameSuffixes: ["T-Shirt", "Drop-shoulder Tee", "Graphic Tee"],
      materials: ["240 GSM Supima Cotton", "Enzyme washed"],
      tags: ["oversized", "streetwear", "cotton", "casual", "trendy"],
      basePrice: 899,
      priceVariance: 400,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Perfect oversized fit. The 240 GSM cotton feels super premium.",
        "Great quality tee. Fabric doesn't shrink after washing.",
      ],
      badges: ["Better Value", "Premium Quality"],
      descriptionTemplate: "Heavyweight oversized tee made from premium Supima cotton. Enzyme-washed for a soft, worn-in feel from day one.",
    },
  ],
  Footwear: [
    {
      namePrefix: "Merino Wool",
      nameSuffixes: ["Runners", "Everyday Sneakers", "Slip-ons"],
      materials: ["Merino Wool Upper", "Bio-based outsole", "Cork insole"],
      tags: ["merino wool", "sustainable", "comfortable", "lightweight", "eco-friendly"],
      basePrice: 3999,
      priceVariance: 1500,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Incredibly comfortable and breathable. The merino wool keeps feet cool.",
        "Best sustainable footwear from India. Super lightweight and odor-resistant.",
      ],
      badges: ["Sustainable", "Premium Quality", "Made in India"],
      descriptionTemplate:
        "Made with natural merino wool and a bio-based outsole. Lightweight, breathable, and built to last.",
    },
    {
      namePrefix: "Leather Derby",
      nameSuffixes: ["Shoes", "Oxford Shoes", "Formal Shoes"],
      materials: ["Full-grain leather", "Leather insole", "Rubber sole"],
      tags: ["leather", "formal", "derby", "oxford", "office"],
      basePrice: 4999,
      priceVariance: 2000,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Premium leather quality. Gets better with age.",
        "Excellent craftsmanship. Very comfortable for all-day wear.",
      ],
      badges: ["Premium Quality", "Handcrafted"],
      descriptionTemplate: "Full-grain leather derbies handcrafted by skilled artisans. A wardrobe investment that ages beautifully.",
    },
    {
      namePrefix: "Canvas Low-top",
      nameSuffixes: ["Sneakers", "Trainers", "Casual Shoes"],
      materials: ["Cotton canvas upper", "Vulcanised rubber sole", "Memory foam insole"],
      tags: ["canvas", "casual", "sneakers", "everyday", "lightweight"],
      basePrice: 1499,
      priceVariance: 500,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Great everyday sneakers. Very comfortable and stylish.",
        "Good quality canvas shoes at an unbeatable price.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "Classic canvas low-tops with a modern twist. Memory foam insole for all-day comfort.",
    },
    {
      namePrefix: "Kolhapuri",
      nameSuffixes: ["Chappal", "Sandals", "Flats"],
      materials: ["Vegetable-tanned leather", "Handwoven straps"],
      tags: ["kolhapuri", "ethnic", "handcrafted", "leather", "traditional"],
      basePrice: 1299,
      priceVariance: 600,
      baseRating: 4.6,
      reviewSummaryTemplates: [
        "Authentic Kolhapuri craftsmanship. Extremely comfortable after a short break-in.",
        "Beautiful handmade chappals. The leather quality is outstanding.",
      ],
      badges: ["Handcrafted", "Artisan Made", "Made in India"],
      descriptionTemplate: "Authentic Kolhapuri sandals handcrafted by artisans in Maharashtra. Made with vegetable-tanned leather.",
    },
    {
      namePrefix: "Trail Running",
      nameSuffixes: ["Shoes", "Sports Shoes", "Running Trainers"],
      materials: ["Mesh upper", "EVA midsole", "Carbon rubber outsole"],
      tags: ["running", "sport", "trail", "athletic", "cushioned"],
      basePrice: 2799,
      priceVariance: 1200,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Great cushioning for long runs. Breathable mesh keeps feet cool.",
        "Excellent grip on trails. Good value for performance shoes.",
      ],
      badges: ["Better Value", "Highly Rated"],
      descriptionTemplate: "High-performance trail running shoes with superior grip and cushioning. Designed for Indian terrain.",
    },
  ],
  Electronics: [
    {
      namePrefix: "True Wireless",
      nameSuffixes: ["Earbuds", "TWS Earphones", "In-ear Buds"],
      materials: ["ABS plastic housing", "Medical-grade silicone tips"],
      tags: ["tws", "wireless", "earbuds", "bluetooth", "anc"],
      basePrice: 1999,
      priceVariance: 1500,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Excellent sound quality for the price. ANC works great in noisy environments.",
        "Great battery life and comfortable fit. Sound rivals premium brands.",
      ],
      badges: ["Better Value", "Highly Rated"],
      descriptionTemplate: "Premium true wireless earbuds with Active Noise Cancellation and up to 30-hour total battery life.",
    },
    {
      namePrefix: "Smart",
      nameSuffixes: ["Speaker", "Bluetooth Speaker", "Portable Speaker"],
      materials: ["Reinforced ABS body", "Fabric grill"],
      tags: ["speaker", "bluetooth", "portable", "waterproof", "360 sound"],
      basePrice: 2499,
      priceVariance: 2000,
      baseRating: 4.2,
      reviewSummaryTemplates: [
        "Impressive 360-degree sound. Built quality feels premium.",
        "Great outdoor speaker. Waterproof and loud enough for parties.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "360-degree sound with deep bass. IPX6 waterproof rating and 12-hour playtime.",
    },
    {
      namePrefix: "Mechanical",
      nameSuffixes: ["Keyboard", "Gaming Keyboard", "Compact Keyboard"],
      materials: ["Aircraft-grade aluminium frame", "PBT keycaps"],
      tags: ["keyboard", "mechanical", "gaming", "typing", "rgb"],
      basePrice: 3999,
      priceVariance: 3000,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Solid build quality. The tactile switches are very satisfying.",
        "Premium keyboard at a fraction of imported price. Great typing experience.",
      ],
      badges: ["Better Value", "Premium Quality"],
      descriptionTemplate: "Mechanical keyboard with hot-swappable switches and aircraft-grade aluminium chassis. RGB backlit.",
    },
    {
      namePrefix: "Wireless",
      nameSuffixes: ["Mouse", "Ergonomic Mouse", "Slim Mouse"],
      materials: ["Matte ABS casing", "Teflon feet pads"],
      tags: ["mouse", "wireless", "ergonomic", "office", "silent"],
      basePrice: 1799,
      priceVariance: 1200,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Comfortable ergonomic design. Long battery life.",
        "Smooth scrolling and precise tracking. Great for all-day office use.",
      ],
      badges: ["Better Value", "Highly Rated"],
      descriptionTemplate: "Ergonomic wireless mouse with 4000 DPI sensor and up to 60 days battery life.",
    },
    {
      namePrefix: "Fast Charging",
      nameSuffixes: ["Power Bank", "Powerbank", "Portable Charger"],
      materials: ["Aerospace aluminium body", "Li-Polymer cells"],
      tags: ["powerbank", "fast charging", "portable", "65w", "lightweight"],
      basePrice: 2299,
      priceVariance: 1500,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Super fast charging. Compact design and premium build.",
        "Excellent power bank with fast PD charging. Slim and light.",
      ],
      badges: ["Better Value", "Premium Quality"],
      descriptionTemplate: "Slim 20000mAh power bank with 65W PD fast charging. Can charge laptops, phones, and tablets.",
    },
  ],
  Audio: [
    {
      namePrefix: "Noise Cancelling",
      nameSuffixes: ["Headphones", "Over-ear Headphones", "Wireless Headphones"],
      materials: ["Memory foam ear cushions", "Aluminium headband"],
      tags: ["headphones", "anc", "wireless", "over-ear", "premium sound"],
      basePrice: 3499,
      priceVariance: 2000,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Excellent ANC and sound quality. Very comfortable for long sessions.",
        "Great alternative to premium imported headphones. Bass is impressive.",
      ],
      badges: ["Better Value", "Highly Rated"],
      descriptionTemplate: "Premium over-ear headphones with Hybrid ANC, 40mm custom drivers, and 60-hour battery life.",
    },
    {
      namePrefix: "Studio",
      nameSuffixes: ["Neckband", "Wireless Earphones", "Neckband Earphones"],
      materials: ["Silicone neckband", "Graphene drivers"],
      tags: ["neckband", "wireless", "bass", "studio", "sports"],
      basePrice: 1299,
      priceVariance: 800,
      baseRating: 4.2,
      reviewSummaryTemplates: [
        "Punchy bass and clear highs. Great for workouts.",
        "Comfortable neckband design with impressive sound quality.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "Wireless neckband with graphene drivers for studio-quality sound. 24-hour battery life.",
    },
    {
      namePrefix: "HiFi",
      nameSuffixes: ["Earphones", "In-ear Monitors", "Wired Earphones"],
      materials: ["Beryllium-coated drivers", "Braided cable"],
      tags: ["wired", "hifi", "audiophile", "in-ear", "studio quality"],
      basePrice: 2999,
      priceVariance: 2000,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Audiophile-grade sound. Remarkable detail and soundstage.",
        "Best wired earphones under 5000. Crystal clear highs and tight bass.",
      ],
      badges: ["Premium Quality", "Highly Rated"],
      descriptionTemplate: "HiFi wired earphones with beryllium-coated drivers. Detachable MMCX cable for versatility.",
    },
    {
      namePrefix: "Soundbar",
      nameSuffixes: ["2.1", "Wireless Soundbar", "Home Theatre"],
      materials: ["MDF wood cabinet", "Cloth-covered grille"],
      tags: ["soundbar", "home theatre", "subwoofer", "bluetooth", "tv"],
      basePrice: 6999,
      priceVariance: 4000,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Great soundbar for the price. Subwoofer delivers deep bass.",
        "Excellent TV companion. Dolby Audio support is a great addition.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "2.1 channel soundbar with wireless subwoofer. Supports Dolby Audio and DTS surround.",
    },
  ],
  Watches: [
    {
      namePrefix: "Minimalist Dial",
      nameSuffixes: ["Watch", "Analog Watch", "Dress Watch"],
      materials: ["Sapphire crystal glass", "Italian leather strap", "316L stainless steel case"],
      tags: ["minimalist", "analog", "dress watch", "sapphire", "leather"],
      basePrice: 5999,
      priceVariance: 4000,
      baseRating: 4.6,
      reviewSummaryTemplates: [
        "Stunning minimalist design. Sapphire crystal adds premium feel.",
        "Beautifully crafted Indian watch. Competes with Swiss brands.",
      ],
      badges: ["Premium Quality", "Handcrafted", "Made in India"],
      descriptionTemplate: "Minimalist timepiece featuring a sapphire crystal glass and Italian leather strap. Swiss-inspired movement.",
    },
    {
      namePrefix: "Advanced",
      nameSuffixes: ["Smartwatch", "Smart Watch Pro", "Smart Fitness Watch"],
      materials: ["Aluminium alloy case", "Fluoroelastomer strap", "Gorilla glass display"],
      tags: ["smartwatch", "fitness", "health", "gps", "amoled"],
      basePrice: 4499,
      priceVariance: 3500,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Feature-packed smartwatch at a great price. AMOLED display is gorgeous.",
        "Excellent health tracking features. Battery lasts over a week.",
      ],
      badges: ["Better Value", "Highly Rated"],
      descriptionTemplate: "Advanced smartwatch with AMOLED display, 100+ sport modes, SpO2 monitoring, and 7-day battery.",
    },
    {
      namePrefix: "Field",
      nameSuffixes: ["Watch", "Automatic Watch", "Expedition Watch"],
      materials: ["Automatic movement", "Nylon NATO strap", "Brushed steel case"],
      tags: ["automatic", "field watch", "nato strap", "mechanical", "vintage"],
      basePrice: 8999,
      priceVariance: 6000,
      baseRating: 4.7,
      reviewSummaryTemplates: [
        "Excellent Indian-made automatic watch. Movement is accurate and smooth.",
        "Great field watch. The quality rivals much more expensive imported watches.",
      ],
      badges: ["Handcrafted", "Premium Quality", "Made in India"],
      descriptionTemplate: "Hand-wound automatic field watch with 42-hour power reserve. Made by Indian watchmakers.",
    },
    {
      namePrefix: "Sports",
      nameSuffixes: ["Chronograph", "Racing Watch", "Sport Watch"],
      materials: ["Mineral crystal", "Silicone strap", "Ion-plated steel case"],
      tags: ["chronograph", "sport", "racing", "bold", "colorful"],
      basePrice: 2999,
      priceVariance: 1500,
      baseRating: 4.2,
      reviewSummaryTemplates: [
        "Bold design with reliable chronograph function.",
        "Great sports watch. Lightweight and water-resistant.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "Bold chronograph with 100m water resistance and tachymeter bezel. Perfect for active lifestyles.",
    },
  ],
  Skincare: [
    {
      namePrefix: "10% Niacinamide",
      nameSuffixes: ["Serum", "Face Serum", "Brightening Serum"],
      materials: ["Niacinamide 10%", "Zinc 1%", "Hyaluronic Acid"],
      tags: ["niacinamide", "pore minimiser", "brightening", "serum", "dermatologist tested"],
      basePrice: 699,
      priceVariance: 300,
      baseRating: 4.6,
      reviewSummaryTemplates: [
        "Visible pore reduction in 4 weeks. Very affordable compared to imported serums.",
        "The best niacinamide serum in India. Skin looks visibly brighter.",
      ],
      badges: ["Better Value", "Dermatologist Tested", "Highly Rated"],
      descriptionTemplate: "10% Niacinamide + 1% Zinc serum that minimises pores, reduces blemishes, and brightens skin tone.",
    },
    {
      namePrefix: "SPF 50+",
      nameSuffixes: ["Sunscreen", "Sunblock", "UV Shield"],
      materials: ["Zinc Oxide", "Titanium Dioxide", "Niacinamide"],
      tags: ["sunscreen", "spf50", "pa++++", "no white cast", "daily"],
      basePrice: 599,
      priceVariance: 200,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "No white cast! Finally a sunscreen that works for Indian skin tones.",
        "Lightweight and non-greasy. Perfect for daily use under makeup.",
      ],
      badges: ["Better Value", "Made for Indian Skin", "Highly Rated"],
      descriptionTemplate: "SPF 50+ PA++++ mineral sunscreen with no white cast. Lightweight formula enriched with Niacinamide.",
    },
    {
      namePrefix: "Vitamin C",
      nameSuffixes: ["Face Wash", "Brightening Cleanser", "Glow Cleanser"],
      materials: ["Vitamin C", "Kojic Acid", "Aloe Vera Extract"],
      tags: ["vitamin c", "brightening", "face wash", "glow", "anti-oxidant"],
      basePrice: 399,
      priceVariance: 200,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Skin feels bright and clean after every wash. Love the vitamin C boost.",
        "Great brightening face wash. Gentle yet effective.",
      ],
      badges: ["Better Value", "Clean Formula"],
      descriptionTemplate: "Brightening face wash with Vitamin C and Kojic Acid for a natural glow. Suitable for all skin types.",
    },
    {
      namePrefix: "Hyaluronic Acid",
      nameSuffixes: ["Moisturiser", "Gel Moisturiser", "Water Cream"],
      materials: ["3x Hyaluronic Acid", "Ceramides", "Peptides"],
      tags: ["hyaluronic acid", "moisturiser", "hydration", "anti-ageing", "lightweight"],
      basePrice: 799,
      priceVariance: 400,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Deeply hydrating without being heavy. Skin feels plump all day.",
        "Best moisturiser I've used. Lightweight and absorbs quickly.",
      ],
      badges: ["Better Value", "Highly Rated", "Dermatologist Tested"],
      descriptionTemplate: "Multi-weight Hyaluronic Acid moisturiser with Ceramides and Peptides. 72-hour hydration.",
    },
    {
      namePrefix: "Retinol",
      nameSuffixes: ["Night Cream", "Anti-ageing Serum", "Renewal Cream"],
      materials: ["0.3% Retinol", "Bakuchiol", "Squalane"],
      tags: ["retinol", "anti-ageing", "night cream", "wrinkles", "skin renewal"],
      basePrice: 899,
      priceVariance: 500,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Visible reduction in fine lines after a month. Great beginner retinol.",
        "Gentle yet effective retinol cream. Skin looks visibly younger.",
      ],
      badges: ["Better Value", "Dermatologist Tested"],
      descriptionTemplate: "Gentle retinol night cream with Bakuchiol for enhanced efficacy. Reduces fine lines and improves texture.",
    },
  ],
  Bags: [
    {
      namePrefix: "Cabin",
      nameSuffixes: ["Trolley", "Carry-on", "Travel Bag"],
      materials: ["Polycarbonate shell", "Aluminium telescoping handle", "TSA-approved lock"],
      tags: ["luggage", "cabin", "trolley", "travel", "lightweight"],
      basePrice: 7999,
      priceVariance: 5000,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Premium cabin luggage at a fraction of imported brand prices. Smooth spinner wheels.",
        "Excellent build quality. The polycarbonate shell is scratch-resistant.",
      ],
      badges: ["Better Value", "Premium Quality"],
      descriptionTemplate: "Lightweight cabin trolley with 360° spinner wheels, aluminium frame, and TSA-approved lock.",
    },
    {
      namePrefix: "Vegan Leather",
      nameSuffixes: ["Backpack", "Laptop Bag", "Work Backpack"],
      materials: ["Vegan leather", "Water-resistant lining", "YKK zippers"],
      tags: ["backpack", "vegan leather", "laptop", "work", "sustainable"],
      basePrice: 3999,
      priceVariance: 2000,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Stunning vegan leather backpack. Fits 15\" laptop perfectly.",
        "Premium look and feel. Very spacious with great organisation.",
      ],
      badges: ["Sustainable", "Premium Quality", "Made in India"],
      descriptionTemplate: "Structured vegan leather backpack with padded 15\" laptop compartment and multiple pockets.",
    },
    {
      namePrefix: "Sustainable",
      nameSuffixes: ["Tote Bag", "Canvas Tote", "Everyday Bag"],
      materials: ["Organic cotton canvas", "Natural leather handles"],
      tags: ["tote", "canvas", "sustainable", "everyday", "eco"],
      basePrice: 1299,
      priceVariance: 700,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Love the sustainable cotton canvas. Sturdy and looks great.",
        "Perfect everyday tote. Fits everything you need.",
      ],
      badges: ["Sustainable", "Handcrafted", "Made in India"],
      descriptionTemplate: "Organic cotton canvas tote with natural leather handles. Spacious, durable, and planet-friendly.",
    },
    {
      namePrefix: "Mini",
      nameSuffixes: ["Crossbody Bag", "Sling Bag", "Shoulder Bag"],
      materials: ["Genuine leather", "Brass hardware", "Suede lining"],
      tags: ["crossbody", "leather", "mini", "going out", "compact"],
      basePrice: 2499,
      priceVariance: 1500,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Beautiful leather crossbody. The brass hardware adds a luxe touch.",
        "Perfect size for essentials. Excellent Indian leather quality.",
      ],
      badges: ["Premium Quality", "Handcrafted", "Made in India"],
      descriptionTemplate: "Compact genuine leather crossbody with adjustable strap and brass-tone hardware.",
    },
    {
      namePrefix: "Office",
      nameSuffixes: ["Messenger Bag", "Briefcase", "Work Bag"],
      materials: ["Full-grain leather", "Laptop padding", "Magnetic closure"],
      tags: ["messenger", "office", "leather", "briefcase", "professional"],
      basePrice: 4999,
      priceVariance: 3000,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Premium leather messenger bag. Perfect for office commute.",
        "Excellent craftsmanship. Ages beautifully with use.",
      ],
      badges: ["Premium Quality", "Handcrafted"],
      descriptionTemplate: "Full-grain leather messenger bag with padded laptop sleeve. Ages gracefully with character.",
    },
  ],
  Jewelry: [
    {
      namePrefix: "Sterling Silver",
      nameSuffixes: ["Ring", "Stackable Ring", "Statement Ring"],
      materials: ["925 Sterling Silver", "Rhodium plating"],
      tags: ["silver", "ring", "minimal", "stackable", "everyday jewelry"],
      basePrice: 1499,
      priceVariance: 1000,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Beautiful sterling silver ring. Doesn't tarnish even after months.",
        "Elegant and minimal design. Very true to size.",
      ],
      badges: ["Certified", "Made in India", "Handcrafted"],
      descriptionTemplate: "925 Sterling Silver ring with rhodium plating for lasting shine. Hallmark certified.",
    },
    {
      namePrefix: "Gold Vermeil",
      nameSuffixes: ["Necklace", "Pendant Necklace", "Layering Necklace"],
      materials: ["18K gold vermeil", "Sterling silver base"],
      tags: ["gold", "necklace", "vermeil", "dainty", "layering"],
      basePrice: 2499,
      priceVariance: 1500,
      baseRating: 4.6,
      reviewSummaryTemplates: [
        "Gorgeous gold vermeil necklace. Very delicate and feminine.",
        "Excellent quality. The gold plating is thick and durable.",
      ],
      badges: ["Premium Quality", "Certified", "Made in India"],
      descriptionTemplate: "18K gold vermeil necklace on sterling silver base. Perfect for layering.",
    },
    {
      namePrefix: "Kundan",
      nameSuffixes: ["Earrings", "Jhumkas", "Chandelier Earrings"],
      materials: ["Kundan stones", "Gold-plated brass", "Semi-precious stones"],
      tags: ["kundan", "ethnic", "jhumka", "traditional", "wedding"],
      basePrice: 1999,
      priceVariance: 2000,
      baseRating: 4.7,
      reviewSummaryTemplates: [
        "Stunning kundan earrings. Perfect for weddings and festivals.",
        "Beautiful traditional craftsmanship. Very lightweight for the size.",
      ],
      badges: ["Handcrafted", "Artisan Made", "Made in India"],
      descriptionTemplate: "Traditional kundan earrings handcrafted by artisans in Jaipur. Perfect for festive occasions.",
    },
    {
      namePrefix: "Lab-grown Diamond",
      nameSuffixes: ["Tennis Bracelet", "Bracelet", "Bangle"],
      materials: ["Lab-grown diamonds", "18K white gold", "VS clarity"],
      tags: ["diamond", "lab grown", "bracelet", "luxury", "sustainable"],
      basePrice: 12999,
      priceVariance: 10000,
      baseRating: 4.6,
      reviewSummaryTemplates: [
        "Stunning lab-grown diamond bracelet. Indistinguishable from natural diamonds.",
        "Excellent value for lab-grown diamonds. Perfect everyday luxury.",
      ],
      badges: ["Premium Quality", "Sustainable", "Certified"],
      descriptionTemplate: "Lab-grown diamond tennis bracelet in 18K white gold. VS clarity, conflict-free, and certified.",
    },
  ],
  Furniture: [
    {
      namePrefix: "Solid Sheesham",
      nameSuffixes: ["Coffee Table", "Side Table", "Centre Table"],
      materials: ["Solid Sheesham wood", "Teak oil finish", "Metal hairpin legs"],
      tags: ["sheesham", "solid wood", "coffee table", "handcrafted", "indian wood"],
      basePrice: 8999,
      priceVariance: 5000,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Beautiful solid sheesham table. The wood grain is gorgeous.",
        "Sturdy and well-made. Exactly as described.",
      ],
      badges: ["Handcrafted", "Made in India", "Solid Wood"],
      descriptionTemplate: "Hand-crafted solid Sheesham wood coffee table with hairpin metal legs. Teak oil finish for natural protection.",
    },
    {
      namePrefix: "Memory Foam",
      nameSuffixes: ["Mattress", "Orthopedic Mattress", "Foam Mattress"],
      materials: ["High-density memory foam", "Adaptive comfort layers", "Breathable cover"],
      tags: ["mattress", "memory foam", "orthopedic", "sleep", "queen size"],
      basePrice: 14999,
      priceVariance: 10000,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Game-changing mattress. Sleep quality improved dramatically.",
        "Perfect firmness balance. No back pain after switching.",
      ],
      badges: ["Better Value", "Certified", "Made in India"],
      descriptionTemplate: "7-zone memory foam mattress with adaptive comfort layers. 100-night free trial included.",
    },
    {
      namePrefix: "Mango Wood",
      nameSuffixes: ["Bookshelf", "Storage Shelf", "Display Shelf"],
      materials: ["Solid Mango wood", "Natural oil finish", "Adjustable shelves"],
      tags: ["bookshelf", "mango wood", "storage", "display", "handcrafted"],
      basePrice: 7499,
      priceVariance: 4000,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Beautiful mango wood shelving. Great craftsmanship.",
        "Very sturdy and well-finished. Holds books and decor perfectly.",
      ],
      badges: ["Handcrafted", "Made in India", "Solid Wood"],
      descriptionTemplate: "Solid mango wood bookshelf with adjustable shelves and natural oil finish. Handcrafted in Rajasthan.",
    },
  ],
  "Home Decor": [
    {
      namePrefix: "Madhubani Art",
      nameSuffixes: ["Print", "Wall Art", "Framed Print"],
      materials: ["Handmade paper", "Natural pigments", "Bamboo frame"],
      tags: ["madhubani", "wall art", "traditional art", "handpainted", "indian art"],
      basePrice: 1499,
      priceVariance: 1000,
      baseRating: 4.7,
      reviewSummaryTemplates: [
        "Stunning authentic Madhubani art. The colours are vibrant.",
        "Beautiful piece that adds a unique Indian touch to any room.",
      ],
      badges: ["Handcrafted", "Artisan Made", "Made in India"],
      descriptionTemplate: "Authentic Madhubani artwork on handmade paper. Created by artisans from Mithila, Bihar.",
    },
    {
      namePrefix: "Ikat",
      nameSuffixes: ["Cushion Cover", "Throw Pillow", "Pillow Cover"],
      materials: ["Hand-woven cotton", "Natural dyes", "Zipper closure"],
      tags: ["ikat", "cushion", "handwoven", "ethnic", "home decor"],
      basePrice: 699,
      priceVariance: 400,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Beautiful ikat patterns. The weaving quality is excellent.",
        "Vibrant colours and sturdy fabric. Great for home decor.",
      ],
      badges: ["Handcrafted", "Made in India", "Artisan Made"],
      descriptionTemplate: "Hand-woven ikat cushion covers using traditional weaving techniques from Andhra Pradesh.",
    },
    {
      namePrefix: "Brass",
      nameSuffixes: ["Vase", "Planter", "Decorative Bowl"],
      materials: ["Handbeaten brass", "Lead-free finish"],
      tags: ["brass", "vase", "traditional", "handbeaten", "home decor"],
      basePrice: 1299,
      priceVariance: 800,
      baseRating: 4.6,
      reviewSummaryTemplates: [
        "Gorgeous handbeaten brass vase. Ages beautifully.",
        "Excellent quality brassware. The craftsmanship is exceptional.",
      ],
      badges: ["Handcrafted", "Artisan Made", "Made in India"],
      descriptionTemplate: "Handbeaten brass vase crafted by master artisans. Each piece has unique, authentic character.",
    },
  ],
  Kitchen: [
    {
      namePrefix: "Stainless Steel",
      nameSuffixes: ["Pressure Cooker", "Cookware Set", "Pan"],
      materials: ["18/10 Stainless Steel", "Tri-ply bottom", "Bakelite handles"],
      tags: ["pressure cooker", "stainless steel", "induction compatible", "kitchen", "cookware"],
      basePrice: 2499,
      priceVariance: 2000,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Excellent quality stainless steel pressure cooker. Very sturdy.",
        "Perfect for Indian cooking. Heats evenly and cleans easily.",
      ],
      badges: ["Better Value", "Made in India", "Premium Quality"],
      descriptionTemplate: "Tri-ply stainless steel pressure cooker with safety valve. Compatible with all hob types including induction.",
    },
    {
      namePrefix: "Non-stick",
      nameSuffixes: ["Tawa", "Dosa Pan", "Griddle"],
      materials: ["Hard-anodised aluminium", "PFOA-free coating", "Soft-grip handle"],
      tags: ["tawa", "non-stick", "dosa", "pan", "PFOA free"],
      basePrice: 1299,
      priceVariance: 800,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Perfect dosas every time! Non-stick coating is excellent.",
        "Great tawa. Heats evenly and the non-stick lasts.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "PFOA-free non-stick tawa ideal for dosas, rotis, and parathas. Hard-anodised for extra durability.",
    },
    {
      namePrefix: "Borosilicate",
      nameSuffixes: ["Casserole", "Storage Container", "Water Bottle"],
      materials: ["High-quality borosilicate glass", "Stainless steel lid"],
      tags: ["borosilicate", "glass", "storage", "microwave safe", "airtight"],
      basePrice: 799,
      priceVariance: 500,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Crystal clear borosilicate glass. Great for storing food.",
        "Excellent quality glass containers. Microwave and oven safe.",
      ],
      badges: ["Premium Quality", "Made in India"],
      descriptionTemplate: "Borosilicate glass casserole with stainless steel lid. Thermal shock resistant and microwave safe.",
    },
  ],
  Fitness: [
    {
      namePrefix: "TPE Yoga",
      nameSuffixes: ["Mat", "Exercise Mat", "Gym Mat"],
      materials: ["TPE foam", "Non-slip surface", "Alignment lines"],
      tags: ["yoga mat", "tpe", "non-slip", "eco friendly", "exercise"],
      basePrice: 1299,
      priceVariance: 800,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Excellent grip and cushioning. Perfect for yoga and pilates.",
        "Great quality yoga mat. The alignment lines are very helpful.",
      ],
      badges: ["Better Value", "Eco-friendly"],
      descriptionTemplate: "6mm TPE yoga mat with alignment lines and non-slip texture. Eco-friendly and lightweight.",
    },
    {
      namePrefix: "Resistance",
      nameSuffixes: ["Band Set", "Training Bands", "Loop Bands"],
      materials: ["Natural latex", "Cotton handles"],
      tags: ["resistance bands", "workout", "home gym", "strength training", "portable"],
      basePrice: 799,
      priceVariance: 400,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Great quality resistance bands. Set of 5 levels is perfect.",
        "Excellent for home workouts. Bands are very durable.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "Set of 5 natural latex resistance bands with varying resistance levels. Perfect for home workouts.",
    },
    {
      namePrefix: "Adjustable",
      nameSuffixes: ["Dumbbell Set", "Weights", "Home Gym Set"],
      materials: ["Cast iron", "Rubber coating", "Chrome handles"],
      tags: ["dumbbells", "weights", "home gym", "adjustable", "strength"],
      basePrice: 3999,
      priceVariance: 3000,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Great quality dumbbells. The rubber coating is thick and durable.",
        "Perfect home gym setup. Adjustable weights are space-saving.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "Cast iron adjustable dumbbell set with rubber coating. Saves space and covers multiple weight ranges.",
    },
  ],
  Perfumes: [
    {
      namePrefix: "Oud",
      nameSuffixes: ["Eau de Parfum", "Attar", "Cologne"],
      materials: ["Agarwood (Oud)", "Rose absolute", "Sandalwood base"],
      tags: ["oud", "oriental", "luxury", "long lasting", "unisex"],
      basePrice: 1999,
      priceVariance: 1500,
      baseRating: 4.6,
      reviewSummaryTemplates: [
        "Rich and complex oud fragrance. Lasts over 12 hours.",
        "Authentic Indian oud fragrance. Rivals luxury imported brands.",
      ],
      badges: ["Premium Quality", "Made in India", "Artisan Made"],
      descriptionTemplate: "Rich oud fragrance with notes of agarwood, rose, and sandalwood. Lasts 12+ hours.",
    },
    {
      namePrefix: "Sandalwood",
      nameSuffixes: ["Perfume", "Body Mist", "Attar"],
      materials: ["Mysore Sandalwood", "Jasmine accord", "Vetiver base"],
      tags: ["sandalwood", "woody", "natural", "mysore", "attar"],
      basePrice: 1299,
      priceVariance: 800,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Authentic Mysore sandalwood fragrance. Absolutely divine.",
        "Beautiful natural sandalwood. Not synthetic at all.",
      ],
      badges: ["Natural", "Made in India", "Premium Quality"],
      descriptionTemplate: "Pure Mysore sandalwood perfume with jasmine and vetiver. Natural and long-lasting.",
    },
    {
      namePrefix: "Floral",
      nameSuffixes: ["Eau de Toilette", "Body Splash", "Fresh Cologne"],
      materials: ["Jasmine absolute", "Tuberose", "Bergamot"],
      tags: ["floral", "jasmine", "fresh", "feminine", "light"],
      basePrice: 999,
      priceVariance: 600,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Light and fresh floral fragrance. Perfect for daytime wear.",
        "Beautiful jasmine-led scent. Very Indian and elegant.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "Fresh floral eau de toilette with jasmine and tuberose heart. Light and versatile.",
    },
  ],
  Eyewear: [
    {
      namePrefix: "Classic Round",
      nameSuffixes: ["Sunglasses", "UV400 Sunglasses", "Tinted Sunglasses"],
      materials: ["Acetate frame", "CR-39 polarised lenses", "Spring hinges"],
      tags: ["sunglasses", "round", "polarised", "uv400", "classic"],
      basePrice: 1999,
      priceVariance: 1200,
      baseRating: 4.4,
      reviewSummaryTemplates: [
        "Great polarised sunglasses at an excellent price.",
        "Sturdy acetate frame and good polarised lenses.",
      ],
      badges: ["Better Value", "UV Protected", "Made in India"],
      descriptionTemplate: "Classic round sunglasses with acetate frame and polarised CR-39 lenses. UV400 protection.",
    },
    {
      namePrefix: "Blue Light",
      nameSuffixes: ["Glasses", "Computer Glasses", "Screen Glasses"],
      materials: ["Titanium frame", "Blue light filter lenses", "Anti-glare coating"],
      tags: ["blue light", "computer glasses", "anti-glare", "titanium", "screen time"],
      basePrice: 1499,
      priceVariance: 1000,
      baseRating: 4.5,
      reviewSummaryTemplates: [
        "Eye strain reduced significantly. Great blue light glasses.",
        "Lightweight titanium frame. Very comfortable for all-day wear.",
      ],
      badges: ["Better Value", "Highly Rated"],
      descriptionTemplate: "Blue light filtering glasses with titanium frame and anti-glare coating. Reduces digital eye strain.",
    },
    {
      namePrefix: "Aviator",
      nameSuffixes: ["Sunglasses", "Classic Aviators", "Pilot Sunglasses"],
      materials: ["Stainless steel frame", "Gradient glass lenses", "Adjustable nose pads"],
      tags: ["aviator", "sunglasses", "classic", "gradient", "stainless steel"],
      basePrice: 1299,
      priceVariance: 800,
      baseRating: 4.3,
      reviewSummaryTemplates: [
        "Classic aviator style at a great price. Build quality is solid.",
        "Great gradient lenses. Lightweight and comfortable to wear.",
      ],
      badges: ["Better Value", "Made in India"],
      descriptionTemplate: "Classic stainless steel aviator sunglasses with gradient glass lenses and spring hinges.",
    },
  ],
};

// ────── Color variants ──────
const colorVariants = [
  { color: "Midnight Black", hex: "#111111" },
  { color: "Pearl White", hex: "#F5F5F5" },
  { color: "Ocean Blue", hex: "#1E40AF" },
  { color: "Forest Green", hex: "#166534" },
  { color: "Terracotta", hex: "#C2410C" },
  { color: "Dusty Rose", hex: "#F9A8D4" },
  { color: "Sage", hex: "#84CC16" },
  { color: "Charcoal", hex: "#374151" },
  { color: "Sand", hex: "#D4A574" },
  { color: "Indigo", hex: "#3730A3" },
  { color: "Olive", hex: "#4D7C0F" },
  { color: "Rust", hex: "#9A3412" },
];

// ────── Helper functions ──────
function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function pickN<T>(arr: T[], n: number): T[] {
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

function randomBetween(min: number, max: number): number {
  return Math.round((Math.random() * (max - min) + min) * 100) / 100;
}

function slugify(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

// ────── Product generator ──────
type Product = {
  id: string;
  brand: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  materials: string[];
  price: number;
  originalPrice: number | null;
  rating: number;
  reviewCount: number;
  productUrl: string;
  imageUrl: string;
  brandUrl: string;
  reviewSummary: string;
  madeInIndia: boolean;
  badges: string[];
};

const products: Product[] = [];
let idCounter = 1;

const categories = Object.keys(categoryTemplates);

for (const category of categories) {
  const templates = categoryTemplates[category];
  const categoryBrands = brands.filter((b) => b.categories.includes(category));
  const images = imagesByCategory[category] || imagesByCategory["Apparel"];

  for (const template of templates) {
    // Generate multiple brand+color+suffix combinations per template
    const targetBrands = categoryBrands.length > 0 ? categoryBrands : brands.slice(0, 5);

    for (const brand of targetBrands) {
      for (const suffix of template.nameSuffixes) {
        for (const colorVariant of pickN(colorVariants, 4)) {
          const productName = `${template.namePrefix} ${suffix}`;
          const fullName = `${productName} — ${colorVariant.color}`;
          const price = Math.round(template.basePrice + randomBetween(-200, template.priceVariance));
          const hasOriginalPrice = Math.random() > 0.6;
          const originalPrice = hasOriginalPrice ? Math.round(price * randomBetween(1.15, 1.4)) : null;
          const rating = Math.round(Math.min(5, template.baseRating + randomBetween(-0.3, 0.3)) * 10) / 10;
          const reviewCount = Math.round(randomBetween(45, 3200));

          const id = `p${String(idCounter).padStart(5, "0")}`;
          idCounter++;

          products.push({
            id,
            brand: brand.name,
            name: fullName,
            description: template.descriptionTemplate + ` Available in ${colorVariant.color}.`,
            category,
            tags: [...template.tags, colorVariant.color.toLowerCase(), brand.name.toLowerCase()],
            materials: template.materials,
            price,
            originalPrice,
            rating,
            reviewCount,
            productUrl: `${brand.url}/products/${slugify(productName)}-${slugify(colorVariant.color)}`,
            imageUrl: `${pick(images)}&sig=${id}`,
            brandUrl: brand.url,
            reviewSummary: pick(template.reviewSummaryTemplates),
            madeInIndia: true,
            badges: pickN(template.badges, Math.min(template.badges.length, 3)),
          });

          if (products.length >= 5000) break;
        }
        if (products.length >= 5000) break;
      }
      if (products.length >= 5000) break;
    }
    if (products.length >= 5000) break;
  }
  if (products.length >= 5000) break;
}

// Ensure exactly 5000 (or close to it)
const finalProducts = products.slice(0, 5000);

fs.writeFileSync(outputPath, JSON.stringify(finalProducts, null, 2));

console.log(`✅ Generated ${finalProducts.length} products → ${outputPath}`);
console.log(`Categories covered: ${[...new Set(finalProducts.map((p) => p.category))].join(", ")}`);
console.log(`Brands covered: ${[...new Set(finalProducts.map((p) => p.brand))].length}`);
