from typing import List, Dict, Any

BRAND_METADATA = {
    "snitch": {
        "name": "Snitch",
        "slug": "snitch",
        "description": "Fast-fashion brand for men offering trendy shirts, trousers, and casual wear.",
        "founded": "2020",
        "founders": "Siddharth Dungarwal",
        "story": "Started as a B2B brand before pivoting to D2C in 2020, Snitch gained national fame on Shark Tank India Season 2, securing an all-shark deal for its ultra-fast trend turnarounds.",
        "websiteUrl": "https://www.snitch.co.in",
        "categories": ["Apparel"],
        "featured": True
    },
    "rare rabbit": {
        "name": "Rare Rabbit",
        "slug": "rare-rabbit",
        "description": "Premium apparel brand for men and women, focusing on high-quality fabrics and unique cuts.",
        "founded": "2015",
        "founders": "Manish Poddar and Akshika Poddar",
        "story": "Launched by House of Three under Manish Poddar, Rare Rabbit redefined Indian premium casual fashion by focusing on sophisticated tailoring, high-quality linen/cotton, and aesthetic styling.",
        "websiteUrl": "https://rarerabbit.in",
        "categories": ["Apparel"],
        "featured": True
    },
    "bombay shirt company": {
        "name": "Bombay Shirt Company",
        "slug": "bombay-shirt-company",
        "description": "India's first custom shirt brand offering tailored linen, cotton, and formal shirts.",
        "founded": "2012",
        "founders": "Akshay Narvekar",
        "story": "Founded to solve the issue of standard sizes not fitting Indian body shapes, BSC offers premium custom tailoring online and in stores using premium fabrics like Giza cotton and French linen.",
        "websiteUrl": "https://bombaytshirtcompany.com",
        "categories": ["Apparel"],
        "featured": True
    },
    "nicobar": {
        "name": "Nicobar",
        "slug": "nicobar",
        "description": "Modern Indian lifestyle brand with organic cotton apparel, jewelry, and earthy home decor.",
        "founded": "2016",
        "founders": "Simran Lal and Raul Rai",
        "story": "Created by the founders of Good Earth, Nicobar targets the modern global Indian, focusing on sustainable, lightweight organic fabrics and minimalist, tropical design language.",
        "websiteUrl": "https://nicobar.com",
        "categories": ["Apparel", "Home Decor"],
        "featured": True
    },
    "the souled store": {
        "name": "The Souled Store",
        "slug": "the-souled-store",
        "description": "Popular pop-culture casual wear brand offering official merchandise and streetwear.",
        "founded": "2013",
        "founders": "Vedang Patel, Aditya Sharma, Rohin Samtaney, and Harsh Lal",
        "story": "Started by four friends with an initial investment of Rs. 1.75 Lakhs, it grew into India's largest pop-culture merchandise brand with official licenses from Marvel, Disney, Warner Bros., and anime studios.",
        "websiteUrl": "https://www.thesouledstore.com",
        "categories": ["Apparel"],
        "featured": True
    },
    "zouk": {
        "name": "Zouk",
        "slug": "zouk",
        "description": "PeTA-approved vegan bags and footwear with modern Indian ikat and jute prints.",
        "founded": "2018",
        "founders": "Disha Singh and Pradeep Krishnakumar",
        "story": "Inspired by a trip to Kutch where Disha realized the huge appeal of local crafts but lack of modern designs, Zouk creates bags and wallets blending traditional Indian motifs with vegan leather.",
        "websiteUrl": "https://www.zouk.co.in",
        "categories": ["Bags", "Footwear"],
        "featured": True
    },
    "mokobara": {
        "name": "Mokobara",
        "slug": "mokobara",
        "description": "Premium luggage and travel bags with minimalist, sleek aesthetics.",
        "founded": "2020",
        "founders": "Sangeet Sarma and Navin Parwal",
        "story": "Set out to bring joy back to travel. Mokobara designs luggage using aerospace-grade German Makrolon Polycarbonate, premium Hinomoto/custom silent wheels, and thoughtful compression compartments, competing directly with Away and Samsonite.",
        "websiteUrl": "https://www.mokobara.com",
        "categories": ["Bags"],
        "featured": True
    },
    "dailyobjects": {
        "name": "DailyObjects",
        "slug": "dailyobjects",
        "description": "Design-focused accessories for laptops, mobile phones, tech organizer bags, and home office setups.",
        "founded": "2012",
        "founders": "Pankaj Garg and Saurabh Gara",
        "story": "Began as a mobile cover store and expanded into a premier lifestyle design studio, creating high-utility desk organizers, canvas tech sleeves, and duffle bags that emphasize material quality.",
        "websiteUrl": "https://www.dailyobjects.com",
        "categories": ["Bags", "Electronics"],
        "featured": True
    },
    "minimalist": {
        "name": "Minimalist",
        "slug": "minimalist",
        "description": "Science-backed, ingredient-focused skincare brand offering affordable serums, moisturizers, and sunscreens.",
        "founded": "2020",
        "founders": "Mohit Yadav and Rahul Yadav",
        "story": "Launched to bring transparency to the Indian beauty industry, Minimalist publishes clinical trial results and details exact active ingredient percentages (e.g. Niacinamide, Salicylic acid), rivaling international giants like The Ordinary.",
        "websiteUrl": "https://beminimalist.co",
        "categories": ["Skincare"],
        "featured": True
    },
    "dot & key": {
        "name": "Dot & Key",
        "slug": "dot-key",
        "description": "Nature-infused skincare focusing on hydration, skin fruit actives, and targeted serums.",
        "founded": "2018",
        "founders": "Suyash Saraf and Anisha Saraf",
        "story": "Acquired by Nykaa, Dot & Key focuses on water-based hydration products and fruity skincare active formulations, offering a sensory and effective alternative to K-Beauty brands.",
        "websiteUrl": "https://www.dotandkey.com",
        "categories": ["Skincare"],
        "featured": True
    },
    "plum": {
        "name": "Plum",
        "slug": "plum",
        "description": "100% vegan, cruelty-free clean beauty and skincare brand.",
        "founded": "2013",
        "founders": "Shankar Prasad",
        "story": "India's first 100% vegan beauty brand. Focused on clean science, sustainability (recycling packaging), and highly rated green tea skincare ranges.",
        "websiteUrl": "https://plumgoodness.com",
        "categories": ["Skincare"],
        "featured": True
    },
    "the derma co": {
        "name": "The Derma Co",
        "slug": "the-derma-co",
        "description": "Dermatologist-designed skincare formulations to treat acne, pigmentation, and open pores.",
        "founded": "2020",
        "founders": "Varun Alagh and Ghazal Alagh (Honasa Consumer)",
        "story": "A subsidiary of Honasa Consumer (Mamaearth), The Derma Co provides active science formulations that focus on specific dermatological concerns under expert guidance.",
        "websiteUrl": "https://thedermacompany.com",
        "categories": ["Skincare"],
        "featured": True
    },
    "boat": {
        "name": "boAt",
        "slug": "boat",
        "description": "India's leading consumer audio brand offering headphones, earbuds, smartwatches, and speakers.",
        "founded": "2016",
        "founders": "Aman Gupta and Sameer Mehta",
        "story": "Started as a cable manufacturer, boAt grew into one of the world's largest wearable brands by marketing 'Bassheads' audio tuning tailored for Indian consumer tastes, utilizing influencers and high-style aesthetics.",
        "websiteUrl": "https://www.boat-lifestyle.com",
        "categories": ["Audio", "Electronics"],
        "featured": True
    },
    "noise": {
        "name": "Noise",
        "slug": "noise",
        "description": "Popular smartwatch and audio accessories brand targeting active, young consumers.",
        "founded": "2014",
        "founders": "Amit Khatri and Gaurav Khatri",
        "story": "Began by selling smartphone covers before entering smart wearables, successfully topping the Indian smartwatch market by offering fitness tracking and premium displays at highly competitive rates.",
        "websiteUrl": "https://www.gonoise.com",
        "categories": ["Electronics", "Watches"],
        "featured": True
    },
    "boult": {
        "name": "Boult",
        "slug": "boult",
        "description": "High-fidelity wireless earbuds, headphones, and smartwatch brand.",
        "founded": "2017",
        "founders": "Varun Gupta and Tarun Gupta",
        "story": "Focused on acoustic engineering and premium finishes, Boult provides high-fidelity, ergonomic neckbands and ear pods competing with JBL and Skullcandy.",
        "websiteUrl": "https://boult.com",
        "categories": ["Audio"],
        "featured": True
    },
    "portronics": {
        "name": "Portronics",
        "slug": "portronics",
        "description": "Innovative and portable digital accessory brand offering chargers, projectors, and adapters.",
        "founded": "2010",
        "founders": "Jasmeet Singh",
        "story": "A pioneer in portable electronics in India, Portronics designs robust, innovative adapters, wireless mice, portable keys, and writing pads targeting local commuters and remote workers.",
        "websiteUrl": "https://www.portronics.com",
        "categories": ["Electronics"],
        "featured": True
    },
    "titan": {
        "name": "Titan",
        "slug": "titan",
        "description": "Tata Group watchmaking heritage, offering timeless dress watches, mechanicals, and smart wearables.",
        "founded": "1984",
        "founders": "Xerxes Desai (founded by Tata Group and TIDCO)",
        "story": "A joint venture between Tata Group and Tamil Nadu Industrial Development Corporation (TIDCO), Titan revolutionized Indian horology by replacing mechanical watches with electronic quartz movements, growing into the 5th largest watch manufacturer globally.",
        "websiteUrl": "https://www.titan.co.in",
        "categories": ["Watches"],
        "featured": True
    },
    "fastrack": {
        "name": "Fastrack",
        "slug": "fastrack",
        "description": "Youth-centric watch, eyewear, and accessories brand offering trendy designs.",
        "founded": "1998",
        "founders": "Xerxes Desai (Titan sub-brand)",
        "story": "Spun off from Titan as a youth-focused brand, Fastrack dominated the teenage accessories market by introducing bold, colorful, and affordable watches and sunglasses.",
        "websiteUrl": "https://www.fastrack.in",
        "categories": ["Watches", "Eyewear"],
        "featured": True
    },
    "bangalore watch company": {
        "name": "Bangalore Watch Company",
        "slug": "bangalore-watch-company",
        "description": "Fine mechanical and automatic watches drawing inspiration from Indian history and aviation.",
        "founded": "2017",
        "founders": "Nirupesh Joshi and Mercy Amalraj",
        "story": "Started by a husband-and-wife duo who returned from tech careers abroad, BWC designs fine automatic watches hand-assembled in Bangalore. They use surgical-grade steel, sapphire crystals, and Japanese/Swiss calibres.",
        "websiteUrl": "https://bangalorewatchcompany.com",
        "categories": ["Watches"],
        "featured": True
    },
    "wakefit": {
        "name": "Wakefit",
        "slug": "wakefit",
        "description": "Home solutions brand offering mattresses, ergonomic chairs, and space-saving solid wood furniture.",
        "founded": "2016",
        "founders": "Ankit Garg and Chaitanya Ramalingegowda",
        "story": "Began as a memory foam mattress direct-to-consumer pioneer and expanded into full home solutions. Known for clinical sleep science testing and affordable sheesham wood furniture.",
        "websiteUrl": "https://www.wakefit.co",
        "categories": ["Furniture"],
        "featured": True
    },
    "wooden street": {
        "name": "Wooden Street",
        "slug": "wooden-street",
        "description": "Custom-made solid wood furniture, sheesham coffee tables, and contemporary decor elements.",
        "founded": "2015",
        "founders": "Lokendra Ranawat, Virendra Ranawat, Dinesh Pratap Singh, and Vikas Baheti",
        "story": "Launched to streamline India's unorganized custom furniture sector. They provide handmade, solid wood furniture built primarily from seasoned Sheesham and Mango wood.",
        "websiteUrl": "https://www.woodenstreet.com",
        "categories": ["Furniture"],
        "featured": True
    },
    "wonderchef": {
        "name": "Wonderchef",
        "slug": "wonderchef",
        "description": "Premium cookware and kitchen appliances co-founded by Chef Sanjeev Kapoor.",
        "founded": "2009",
        "founders": "Chef Sanjeev Kapoor and Ravi Saxena",
        "story": "Brings global standards of design and material safety (like PFOA-free coatings and German quality standards) to Indian kitchens, co-created by India's most celebrated masterchef.",
        "websiteUrl": "https://www.wonderchef.com",
        "categories": ["Kitchen"],
        "featured": True
    },
    "borosil": {
        "name": "Borosil",
        "slug": "borosil",
        "description": "Pioneers in high-quality glassware, kitchen gadgets, and insulated tumblers.",
        "founded": "1962",
        "founders": "Dr. Lele (under Kheruka family leadership)",
        "story": "Initially set up to manufacture industrial borosilicate glassware, it transitioned under the Kheruka family to become the gold standard of microwave-safe glassware, lunchboxes, and kitchen appliances in India.",
        "websiteUrl": "https://www.borosil.com",
        "categories": ["Kitchen"],
        "featured": True
    },
    "giva": {
        "name": "GIVA",
        "slug": "giva",
        "description": "Hallmark-certified 925 sterling silver, gold-plated minimal jewelry, and necklaces for daily wear.",
        "founded": "2019",
        "founders": "Ishendra Agarwal, Nikita Prasad, and Sachin Shetty",
        "story": "Founded to solve the lack of options in premium, affordable daily-wear fine jewelry for women, GIVA specializes in authentic, certified 925 silver designs.",
        "websiteUrl": "https://www.giva.co",
        "categories": ["Jewelry"],
        "featured": True
    },
    "lenskart": {
        "name": "Lenskart",
        "slug": "lenskart",
        "description": "Omnichannel eyewear giant offering design-oriented eyeglasses, computer lenses, and sunglasses.",
        "founded": "2010",
        "founders": "Peyush Bansal, Amit Chaudhary, and Sumeet Kapahi",
        "story": "Disrupted the offline optical shop cartel by manufacturing its own high-quality lenses and frames. They offer automated German eye testing and a virtual 3D try-on portal.",
        "websiteUrl": "https://www.lenskart.com",
        "categories": ["Eyewear"],
        "featured": True
    },
    "bella vita": {
        "name": "Bella Vita",
        "slug": "bella-vita",
        "description": "Affordable luxury perfume oils, attars, organic fragrances, and body sprays.",
        "founded": "2018",
        "founders": "Aakash Anand",
        "story": "Began as a natural skincare brand before pivoting to fragrance, carving a niche by selling high-concentration luxury EDPs and perfume oils at a fraction of French import prices.",
        "websiteUrl": "https://bellavitaorganic.com",
        "categories": ["Perfumes"],
        "featured": True
    },
    "skinn by titan": {
        "name": "Skinn by Titan",
        "slug": "skinn-by-titan",
        "description": "Premium French-crafted perfumes designed for the Indian climate and sensory preferences.",
        "founded": "2013",
        "founders": "Titan Company Ltd (Tata Group)",
        "story": "Collaborates with world-renowned French perfumers (like Alberto Morillas and Olivier Pescheux) to manufacture premium, long-lasting fragrances designed specifically to withstand India's humid weather conditions.",
        "websiteUrl": "https://www.titan.co.in",
        "categories": ["Perfumes"],
        "featured": True
    },
    "cultsport": {
        "name": "Cultsport",
        "slug": "cultsport",
        "description": "Activewear and sports fitness equipment brand by Cure.fit, offering running shoes and gear.",
        "founded": "2019",
        "founders": "Mukesh Bansal and Ankit Nagori",
        "story": "Spun off from Cult.fit, Cultsport focuses on functional, lightweight, sweat-wicking activewear and smart fitness machines synced with the Cult ecosystem.",
        "websiteUrl": "https://cultsport.com",
        "categories": ["Fitness"],
        "featured": True
    },
    "boldfit": {
        "name": "Boldfit",
        "slug": "boldfit",
        "description": "Popular fitness accessories, yoga mats, resistance bands, and workout supplements.",
        "founded": "2018",
        "founders": "Pallav Bihani",
        "story": "Started by a young entrepreneur to make high-quality home workout gear accessible, Boldfit grew rapidly during the fitness shift of 2020 by offering durable yoga mats and accessories.",
        "websiteUrl": "https://boldfit.in",
        "categories": ["Fitness"],
        "featured": True
    },
    "comet": {
        "name": "Comet",
        "slug": "comet",
        "description": "Lifestyle sneaker brand offering retro and streetwear designs for Gen Z.",
        "founded": "2023",
        "founders": "Utkarsh Gupta and Dishant Daryani",
        "story": "Set out to disrupt the Indian lifestyle sneaker market by designing bold, premium streetwear shoes locally, avoiding high international pricing.",
        "websiteUrl": "https://www.wearcomet.com",
        "categories": ["Footwear"],
        "featured": True
    },
    "neeman's": {
        "name": "Neeman's",
        "slug": "neemans",
        "description": "Eco-friendly, sustainable footwear brand utilizing Merino wool and recycled materials.",
        "founded": "2018",
        "founders": "Taran Chhabra and Amar Preet Singh",
        "story": "Pioneered sustainable shoes in India by using renewable resources like Australian Merino wool, recycled plastic bottles, and organic cotton to create comfortable footwear.",
        "websiteUrl": "https://neemans.com",
        "categories": ["Footwear"],
        "featured": True
    },
    "chumbak": {
        "name": "Chumbak",
        "slug": "chumbak",
        "description": "Quirky, color-themed lifestyle brand offering clothing, accessories, and home decor.",
        "founded": "2010",
        "founders": "Shubhra Chadda and Vivek Prabhakar",
        "story": "Began as an India-themed souvenir brand and grew into a massive lifestyle entity characterized by bright prints and handcraft-inspired aesthetics.",
        "websiteUrl": "https://www.chumbak.com",
        "categories": ["Home Decor", "Bags", "Apparel"],
        "featured": True
    },
    "bombay perfumery": {
        "name": "Bombay Perfumery",
        "slug": "bombay-perfumery",
        "description": "Independent luxury fragrance house highlighting distinct Indian ingredients.",
        "founded": "2016",
        "founders": "Manan Gandhi",
        "story": "Collaborates with global perfumers to formulate fine modern scents highlighting Indian spices, flowers, and ingredients like ginger and pepper.",
        "websiteUrl": "https://www.bombayperfumery.com",
        "categories": ["Perfumes"],
        "featured": True
    }
}

def get_brand_details(name: str) -> Dict[str, Any]:
    name_lower = name.lower()
    if name_lower in BRAND_METADATA:
        return BRAND_METADATA[name_lower]
        
    # Attempt substring matching
    for bname, meta in BRAND_METADATA.items():
        if bname in name_lower or name_lower in bname:
            return meta
            
    return {
        "name": name,
        "slug": name_lower.replace(" ", "-"),
        "description": f"Premium Indian brand offering quality {name} alternatives.",
        "founded": "2018",
        "founders": "Unknown",
        "story": f"A quality Indian brand specializing in {name}.",
        "websiteUrl": "",
        "categories": [],
        "featured": False
    }

def get_all_brands() -> List[Dict[str, Any]]:
    return list(BRAND_METADATA.values())
