__all__ = (
    "artistic_style_choices",
    "artistic_styles",
    "eye_color_choices",
    "hair_color_choices",
    "identity_choices",
    "reading_level_choices",
    "skin_color_choices",
)

# Possible eye colors
eye_color_choices = [
    "amber",
    "blue",
    "brown",
    "gray",
    "green",
    "hazel",
    "violet",
]

# Possible hair colors
hair_color_choices = [
    "auburn",
    "black",
    "blonde",
    "brown",
    "gray",
    "red",
    "white",
]

# Possible skin tones
skin_color_choices = [
    "brown",
    "dark",
    "ebonyfair",
    "light",
    "medium",
    "olive",
    "porcelain",
    "tan",
]

# Possible identity options
identity_choices = [
    "alien",
    "animal",
    "boy",
    "cat",
    "dog",
    "dragon",
    "dwarf",
    "elf",
    "fairy",
    "female",
    "ghost",
    "gnome",
    "girl",
    "goblin",
    "human",
    "king",
    "male",
    "man",
    "ogre",
    "orc",
    "pirate",
    "prince",
    "princess",
    "queen",
    "teacher",
    "unicorn",
    "vampire",
    "witch",
    "wizard",
    "woman",
    "robot",
]

reading_level_choices = ["early", "middle", "advanced", "balanced"]

# Possible style options
artistic_styles: dict[str, str] = {
    # Art historical period/movement
    "Pre-Raphaelite Brotherhood": "lush botanical detail, jewel-like color palette, medieval romantic setting, intricate natural elements, ethereal lighting",  # noqa
    "Art Nouveau": "flowing organic lines, decorative floral and vine motifs, harmonious pastel or muted tones, ornamental framing, sinuous composition",  # noqa
    "Symbolism": "dreamlike atmosphere, allegorical objects, soft focus mist, muted or monochrome palette, contemplative mood",  # noqa
    "Romanticism": "dramatic skies, sweeping landscapes, heightened emotion, painterly brushwork, sense of sublime grandeur",  # noqa
    "Realism": "natural lighting, lifelike textures, unidealized everyday scenes, subdued color scheme, high detail fidelity",  # noqa
    "Impressionism": "visible brushstrokes, dappled light effects, vibrant yet soft colors, outdoor (“en plein air”) scene, fleeting moment",  # noqa
    "Post-Impressionism": "structured forms, bold outlines, expressive color contrasts, simplified shapes, tactile brushwork",  # noqa
    "Art Deco": "geometric symmetry, high-contrast metallic accents, streamlined forms, bold color blocks, glamorous sheen",  # noqa
    "Expressionism": "distorted perspective, intense color saturation, emotive exaggeration, raw brush marks, psychological tension",  # noqa
    "Cubism": "fragmented geometry, overlapping planes, multiple viewpoints, muted earth tones or limited palette, abstract deconstruction",  # noqa
    "Futurism": "dynamic motion blur, diagonal thrust lines, metallic sheen, urban machinery, sense of speed",  # noqa
    "Dada": "collage of found objects, torn paper edges, haphazard typography, absurd juxtapositions, playful chaos",  # noqa
    "Surrealism": "bizarre juxtapositions, floating objects, hyperreal detail with impossible elements, dream-logic composition",  # noqa
    "Abstract Expressionism": "large-scale canvas, spontaneous drips and splatters, bold gestural strokes, high-contrast color fields, raw texture",  # noqa
    "Pop Art": "flat blocks of bright primary colors, graphic halftone dots, bold outlines, mass-media imagery, ironic twist",  # noqa
    "Op Art": "precise repeating patterns, high-contrast black and white (or bright complementary colors), optical illusion effect, geometric rigor",  # noqa
    "Minimalism": "extremely reduced forms, large areas of negative space, single neutral tone or monochrome, clean lines, austere composition",  # noqa
    "Neo-Expressionism": "raw figurative forms, heavy impasto, intense color clashes, energetic brushwork, emotionally charged subject",  # noqa
    "Digital/Generative Art": "algorithmic patterns, fluid distortions, glitch effects, vibrant gradients, procedural complexity",  # noqa
    "Contemporary Street Art": "bold stencil shapes, spray-paint texture, urban wall setting, high-contrast color pops, rebellious graffiti flair",  # noqa
    # Artist-specific themes
    "M.C. Escher": "mathematical precision, impossible architecture, interlocking tessellations, surreal geometry, recursive patterns",  # noqa
    "J.W. Waterhouse": "mythological femininity, flowing fabrics, tranquil waters, romantic pre-Raphaelite atmosphere, floral details",  # noqa
    "Gustav Klimt": "ornamental gold leaf, flattened perspective, sensual figurative subjects, mosaic textures, art nouveau elegance",  # noqa
    "Rene Magritte": "surreal paradoxes, faceless figures, floating objects, poetic absurdity, dreamlike stillness",  # noqa
    "Vardges Sureniants": "oriental mysticism, Armenian historical themes, vibrant ethnic detail, dramatic figures, deep symbolism",  # noqa
}
artistic_style_choices: list[str] = list(artistic_styles.keys())

# TODO: Use this
mediums: dict[str, str] = {
    # Traditional Media / Finish
    "oil painting": "rich impasto textures, deep saturated colors, visible canvas weave, warm varnish glow, dramatic chiaroscuro lighting",
    "watercolor painting": "soft bleeding edges, translucent layered washes, delicate brush strokes, grainy paper texture, gentle diffuse light",
    "acrylic painting": "bold, opaque color blocks, sharp outlines, matte or satin finish, high color vibrancy, flat graphic quality",
    "pastel drawing": "velvety texture, subtle blending, hazy light effect, soft color transitions, visible dust on the paper",
    "charcoal sketch": "high-contrast monochrome, smudged shadows, fine wispy lines, rough paper grain, unfinished and raw aesthetic",
    "ink wash painting": "monochromatic ink gradient, fluid and spontaneous brush economy, ethereal atmosphere, subtle grey tones",
    "stained glass": "thick lead lines (cames), deep jewel-tone colors, prismatic light diffraction, segmented geometric or figurative shapes",
    "fresco painting": "dry, matte pigment, slightly rough plaster texture, muted earth-tone palette, large-scale mural composition",

    # Photographic Mediums
    "collodion photograph": "wet plate look, long exposure blur, subtle silver tarnish, distinct vignetting, shallow depth of field, mid-19th century aesthetic",
    "photo-realistic photograph": "ultra-sharp focus, granular skin detail, natural lens flares, shallow depth of field (bokeh), commercial lighting setup",
    "cinematic shot": "wide-screen aspect ratio, dramatic rim lighting, film grain texture, deep shadows, color grading (e.g., teal and orange), dynamic composition",
    "macro photography": "extreme close-up detail, exaggerated texture, very shallow depth of field, sharp foreground subject, illuminated by focused light",
    "telephoto lens shot": "compressed perspective, stacked background layers, flat depth of field, tight framing of the subject",
    "black and white photography": "high-contrast grayscale, dramatic tonal range, deep shadows and bright highlights, timeless and stark emotional quality",

    # Rendering Styles / Digital Finish
    "low poly": "simple, angular geometry, clear face edges, flat shaded textures, vibrant saturated colors, 3D rendering aesthetic",
    "voxel art": "blocky, cube-based structure, pixelated 3D look, low resolution, distinct grid lines, video game aesthetic",
    "cel-shading": "hard-edged black outlines, flat blocks of color, limited color palette, anime/cartoon aesthetic, minimal blending",
    "digital matte painting": "hyper-detailed, seamless blend of photo textures and painted elements, epic scale, realistic atmospheric effects, high resolution",
    "vector illustration": "perfectly smooth curves, solid fill colors, no texture or brush detail, scalable and graphic style",
    "holographic": "rainbow color spectrum refraction, shimmering light trails, translucent material, futuristic digital projection effect",
    "3D render": "smooth surface modeling, ray-traced shadows, physically based rendering (PBR) textures, polished studio lighting",
}

# Possible story template options
story_templates: dict[str, str] = {
    # A small, curious protagonist discovers profound truths and connections
    # by paying attention to the seemingly insignificant things or beings in
    # their ordinary world, learning what it truly means to "see with the
    # heart".
    "The Whispers of the Overlooked": """Craft a deeply engaging and allegorical tale in a Gentle Poetic Fable style. The story should resonate with the quiet wisdom and tender melancholy of The Little Prince.
    **Protagonist**: Introduce a young, inquisitive child (e.g., named Lila who loves to collect fallen leaves, or Sam who wonders where the wind sleeps) OR a small, gentle creature (e.g., a solitary firefly searching for its own kind of light, or a tiny seed dreaming of the sky). This character feels a subtle sense of wonder or a quiet question about the world.
    **Setting**: An intimate, seemingly ordinary place that holds hidden beauty and quiet secrets (e.g., a forgotten corner of a garden, the edge of a quiet pond at twilight, an attic filled with dusty memories, a single, patient tree).
    **Thematic Focus**:
    - **The Beauty of Unseen Connections**: Explore how our protagonist, through innocent observation and gentle interaction, discovers the invisible threads that link them to something or someone else (e.g., a shy snail, a wilting flower, a distant star reflected in a puddle, the silent growth of a plant).
    - **Essential Truths Revealed**: Through simple dialogue (if any) or the protagonist’s internal reflections, unveil profound yet simple truths about loneliness, friendship, responsibility, loss, beauty, or what it means to truly care for something.
    - **Seeing with the Heart**: Emphasize the idea that what is essential is often invisible to the eye and can only be perceived through empathy, patience, and love.
    **Narrative Arc & Engagement**:
    - The protagonist encounters something small, overlooked, or seemingly mundane.
    - Driven by gentle curiosity or a quiet longing, they spend time with it, observe it, or try to understand it.
    - Through this interaction, a simple yet profound lesson or connection is revealed, perhaps tinged with a gentle sadness but ultimately offering hope or a deeper understanding.
    - The story should evoke a sense of whimsical wonder (e.g., the dewdrop holds a universe, the wind carries forgotten songs) and quiet awe.
    **Language & Tone**:
    - Employ a gentle, poetic voice.
    - Use clear, straightforward language, easily understood by young readers (ages 5-10), but rich with simple, evocative imagery and symbolism.
    - The tone should be tender, reflective, and imbued with a soft melancholy that resolves into a hopeful understanding.
    **Desired Impact**: The story should prompt the reader to reflect on what truly matters, leaving them with a warm, contemplative feeling, a sense of deep emotional resonance, and a renewed appreciation for the quiet wonders of the everyday world. It should feel like a precious secret shared.
    """,  # noqa
    # A character with a deep yearning or a seemingly impossible dream learns
    # that the "distance" to their goal is not physical, but a matter of
    # perception, belief, and inner growth, discovering that the journey
    # itself holds the destination.
    "The Journey to the Unseen Horizon": """Create a profoundly engaging and allegorical narrative in an Uplifting Spiritual Journey style. The story should capture the inspiring essence and sense of boundless possibility found in tales like There's No Such Place As Far Away.
    **Protagonist**: Introduce a character (e.g., a young bird named Pip who dreams of flying to the moon, a child named Leo who wishes to understand the language of the stars, or a little stream named Whisper longing to reach the great ocean) who holds a powerful, seemingly unattainable desire or feels a call towards something beyond their current reach.
    **The "Far Away" Goal**: This goal should be symbolic of a deeper aspiration – freedom, understanding, belonging, or realizing one's true potential.
    **Thematic Focus**:
    - **Transcending Perceived Limitations**: The protagonist initially believes their dream is impossible due to perceived obstacles (too small, too far, no one has done it before). The story explores how these limitations are primarily internal.
    - **The Power of Belief and Vision**: Emphasize how unwavering belief, focused intention, and the courage to pursue one's unique path can reshape reality and make the impossible possible.
    - **Self-Discovery on the Journey**: The journey towards the goal is more important than the arrival. Each step, challenge, or encounter teaches the protagonist something vital about themselves and the nature of their dream.
    **Narrative Arc & Engagement**:
    - The protagonist passionately articulates or feels their "far away" dream.
    - They encounter initial doubts, obstacles, or the skepticism of others (if applicable, gently portrayed).
    - Through an inspiring encounter (e.g., with a wise old creature, a guiding star, the wind itself) or a profound inner realization, they begin to understand that the "distance" is a matter of perspective or inner state.
    - The protagonist learns to "fly" or "reach" not just with physical effort, but with their heart, mind, or spirit, discovering that what they sought was, in a way, already within them or accessible through a change in understanding.
    - The story should culminate in a moment of joyful realization, freedom, and empowerment.
    **Language & Tone**:
    - Employ clear, direct, and uplifting prose.
    - Use language simple enough for young readers (ages 5-10) to grasp the core message of hope and possibility, while still conveying profound ideas through allegory.
    - The tone should be inspiring, hopeful, and filled with a sense of boundless possibility and wonder.
    **Desired Impact**: The story should leave the reader feeling empowered, reflective, and imbued with the belief that their own dreams, no matter how distant they seem, are worth pursuing. It should ignite a spark of inner freedom and the joy of self-realization.
    """,  # noqa
}

# Possible story styles options
story_styles: dict[str, str] = {
    "Gentle Poetic Fable": "Narrate with a gentle, poetic voice, exploring profound themes like love, loss, and meaning through simple allegory and a child's innocent yet wise perspective. *Employ clear, straightforward language, easily understood by young readers (ages 5-10), to* weave a tale rich in symbolism, focusing on the search for essential truths and the beauty of unseen connections. Infuse the story with a sense of whimsical wonder and a touch of tender melancholy, ultimately offering a message of hope. Prompt the reader to reflect on what truly matters, evoking quiet awe and deep emotional resonance.",  # noqa
    "Uplifting Spiritual Journey": "Craft an inspiring and allegorical narrative focused on self-discovery, the pursuit of dreams, and transcending perceived limitations. Employ clear, direct, and uplifting prose, *using language simple enough for young readers (ages 5-10) to grasp the core message,* to chronicle an individual's journey towards inner freedom and spiritual growth. Emphasize the character's unwavering determination, the joy of breaking free from conformity, and the profound satisfaction of realizing one's unique potential. Aim to leave the reader feeling empowered, reflective, and filled with a sense of boundless possibility.",  # noqa
    "Spirited Childhood Tale": "Tell a heartwarming, humorous, and engaging story capturing the world through a child's eyes, full of adventure, mischief, and keen observations. Use simple, direct, and lively language, *perfectly suited for engaging children aged 5-10,* to bring to life memorable, quirky characters with strong personalities. Focus on themes of friendship, family, everyday escapades, and a child's innate sense of justice and empathy. Infuse the narrative with warmth and charm, making the reader laugh, feel a sense of joyful nostalgia, and connect deeply with the characters' spirited experiences.",  # noqa
    "Sparse Stoic Prose": "Write with sparse, direct prose, conveying deep emotion and meaning through understatement (the 'iceberg theory'). Focus on themes of courage, resilience, and dignity in the face of adversity, often in a struggle against nature or overwhelming odds. Use simple, declarative sentences *that are easily digestible for children aged 5-10*, and vivid, unadorned descriptions. Create a powerful sense of stoicism and the quiet strength of the human spirit, leaving the reader to infer much of the underlying emotional landscape and the weight of unspoken truths, *even if the youngest readers primarily grasp the surface story.*",  # noqa
    "Dark Whimsical Humor": "Craft a story filled with fantastical elements, dark humor, and a touch of the grotesque, often from a child's perspective triumphing over cruel or absurd adults. Employ inventive language, playful neologisms, *all while ensuring the vocabulary and concepts are accessible and delightful for children aged 5-10,* and unexpected plot twists. Create memorable, often exaggerated characters, both delightfully good and repulsively villainous. While whimsical and highly entertaining, subtly weave in moral undertones about fairness, kindness, and the satisfying comeuppance of the wicked. Aim to delight, amuse, and perhaps slightly unsettle the reader with imaginative and mischievous storytelling.",  # noqa
    "Playful Poignant Verse": "Compose with playful, poignant, and deceptively simple verse or prose, *using vocabulary and sentence structures that resonate with young children (ages 5-10),* often accompanied by a whimsical or slightly melancholic tone. Explore themes of childhood, imagination, unconventional perspectives, and the bittersweet realities of life through clever wordplay, humorous situations, and surprising turns of thought. The narrative should spark curiosity and reflection, leaving the reader with a smile and a gentle nudge towards seeing the world differently, embracing both its silliness and its subtle truths.",  # noqa
    "Rhythmic Moral Fun": "Create a rhythmically engaging and wildly imaginative narrative using playful rhymes, invented words, *and overall language designed to captivate and be easily followed by children aged 5-10,* and fantastical creatures or settings. The story should convey a simple, positive moral or social message with lightheartedness and infectious energy. Focus on vibrant, nonsensical fun that captivates the reader's ear and eye (even in text), encouraging a sense of joy, creativity, and the importance of individuality or community.",  # noqa
}
