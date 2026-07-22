#!/usr/bin/env python3
import os
import json
import glob
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, '_templates')
PROJECTS_DIR = os.path.join(BASE_DIR, '_projects')
OUTPUT_DIR = BASE_DIR
PROJECTS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'projects')

def load_template(name):
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        print(f"Error: Template {name} not found.")
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_projects():
    projects = []
    project_files = glob.glob(os.path.join(PROJECTS_DIR, '*.json'))
    for file_path in project_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                projects.append(data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    # Sort projects by slug or title
    projects.sort(key=lambda x: x.get('title', ''))
    return projects

def render_base(title, content, active_tab=""):
    base_html = load_template('base.html')
    
    # Replace active tab tokens
    tabs = ['home', 'projects', 'gallery', 'about']
    for tab in tabs:
        active_class = "active" if tab == active_tab else ""
        base_html = base_html.replace(f"{{{{nav_active_{tab}}}}}", active_class)
        
    base_html = base_html.replace("{{title}}", title)
    base_html = base_html.replace("{{content}}", content)
    return base_html

def build_index(projects):
    featured = [p for p in projects if p.get('featured', False)]
    # Check for explicit hero project, otherwise use first featured
    hero_project = next((p for p in projects if p.get('hero', False)), None)
    if not hero_project:
        hero_project = featured[0] if featured else (projects[0] if projects else None)
    
    hero_html = ""
    if hero_project:
        hero_html = f"""
        <div class="container hero-wrapper">
            <section class="hero-section">
                <div class="hero-image-container">
                    <img src="{hero_project['hero_image']}" alt="{hero_project['title']}" class="hero-image">
                </div>
            </section>
        </div>
        """
        
    statement_html = """
    <section class="statement-section">
        <div class="container">
            <h2 class="statement-text">Artisanal furniture combining modern sculptural forms with traditional joinery, handcrafted in the Hudson Valley.</h2>
        </div>
    </section>
    """
    
    # Featured grid
    grid_items = []
    for p in featured[:3]: # limit to top 3 featured
        grid_items.append(f"""
        <article class="project-card">
            <a href="/projects/{p['slug']}.html" class="project-card-image-link">
                <img src="{p['hero_image']}" alt="{p['title']}" class="project-card-image" loading="lazy">
            </a>
            <div class="project-card-info">
                <div>
                    <h3 class="project-card-title">{p['title']}</h3>
                    <span class="project-card-category">{p['category']}</span>
                </div>
                <a href="/projects/{p['slug']}.html" class="project-card-link">View Detail</a>
            </div>
        </article>
        """)
        
    featured_html = f"""
    <section class="section-padding container">
        <div class="section-header">
            <div>
                <h2 class="section-title">Selected Work</h2>
                <span class="section-subtitle">Featured Studio Pieces</span>
            </div>
            <a href="/projects.html" class="btn btn-outline" style="padding: 0.5rem 1.5rem; font-size: 0.8rem;">View All</a>
        </div>
        <div class="projects-grid">
            {"".join(grid_items)}
        </div>
    </section>
    """
    
    full_content = hero_html + statement_html + featured_html
    rendered = render_base("Home", full_content, active_tab="")
    
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)
    print("Built index.html")

def build_projects_list(projects):
    grid_items = []
    for p in projects:
        grid_items.append(f"""
        <article class="project-card">
            <a href="/projects/{p['slug']}.html" class="project-card-image-link">
                <img src="{p['hero_image']}" alt="{p['title']}" class="project-card-image" loading="lazy">
            </a>
            <div class="project-card-info">
                <div>
                    <h3 class="project-card-title">{p['title']}</h3>
                    <span class="project-card-category">{p['category']}</span>
                </div>
                <a href="/projects/{p['slug']}.html" class="project-card-link">View Detail</a>
            </div>
        </article>
        """)
        
    content = f"""
    <section class="section-padding container">
        <div class="section-header">
            <div>
                <h1 class="section-title">All Projects</h1>
                <span class="section-subtitle">The Complete Collection</span>
            </div>
        </div>
        <div class="projects-grid">
            {"".join(grid_items)}
        </div>
    </section>
    """
    
    rendered = render_base("Projects", content, active_tab="projects")
    with open(os.path.join(OUTPUT_DIR, 'projects.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)
    print("Built projects.html")

def build_project_details(projects):
    os.makedirs(PROJECTS_OUTPUT_DIR, exist_ok=True)
    template = load_template('project.html')
    
    for p in projects:
        # Create minor detail images HTML
        detail_images_html = ""
        # The first image is usually the hero, detail images are the rest
        detail_images = p.get('images', [])[1:] if len(p.get('images', [])) > 1 else []
        for img_path in detail_images:
            detail_images_html += f"""
            <div class="project-detail-img-wrapper">
                <img src="{img_path}" alt="{p['title']} Detail" class="project-detail-img" loading="lazy">
            </div>
            """
            
        # Render project content
        project_content = template
        project_content = project_content.replace("{{title}}", p.get('title', ''))
        project_content = project_content.replace("{{category}}", p.get('category', ''))
        project_content = project_content.replace("{{description}}", p.get('description', ''))
        project_content = project_content.replace("{{materials}}", p.get('materials', ''))
        project_content = project_content.replace("{{dimensions}}", p.get('dimensions', ''))
        project_content = project_content.replace("{{hero_image}}", p.get('hero_image', ''))
        project_content = project_content.replace("{{project_images}}", detail_images_html)
        
        rendered = render_base(p.get('title', ''), project_content, active_tab="projects")
        
        out_path = os.path.join(PROJECTS_OUTPUT_DIR, f"{p['slug']}.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print(f"Built projects/{p['slug']}.html")

def build_gallery(projects):
    # Collect all images from all projects, plus standard names
    gallery_items = []
    
    # Predefined descriptions for images to give an artisanal editorial touch
    captions = {
        "chair-wood-leather-back.jpg": "Chair No. 1 - Profile",
        "chair-wood-leather-detail.jpg": "Chair No. 1 - Joint Detail",
        "chair-blue-cork.jpg": "Chair No. 2 - Plywood & Cork",
        "daybed-detail.jpg": "Daybed No. 1 - Walnut Frame Detail"
    }
    
    # Search for all image files in assets/images/
    images_dir = os.path.join(BASE_DIR, 'assets', 'images')
    if os.path.exists(images_dir):
        for img_name in sorted(os.listdir(images_dir)):
            if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                caption = captions.get(img_name, img_name.replace('-', ' ').split('.')[0].title())
                gallery_items.append({
                    "src": f"/assets/images/{img_name}",
                    "caption": caption
                })
                
    grid_items = []
    for item in gallery_items:
        grid_items.append(f"""
        <div class="gallery-item">
            <img src="{item['src']}" alt="{item['caption']}" class="gallery-img" loading="lazy">
            <div class="gallery-overlay">
                <span class="gallery-caption">{item['caption']}</span>
            </div>
        </div>
        """)
        
    content = f"""
    <section class="section-padding container">
        <div class="section-header">
            <div>
                <h1 class="section-title">Gallery</h1>
                <span class="section-subtitle">Visuals from the Workshop & Collection</span>
            </div>
        </div>
        <div class="gallery-grid">
            {"".join(grid_items)}
        </div>
    </section>
    """
    
    rendered = render_base("Gallery", content, active_tab="gallery")
    with open(os.path.join(OUTPUT_DIR, 'gallery.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)
    print("Built gallery.html")

def build_about():
    content = """
    <section class="about-section container">
        <div class="about-grid">
            <div class="about-image-wrapper">
                <img src="/assets/images/chair-wood-leather-back.jpg" alt="Jared Alon Studio" class="about-image">
            </div>
            <div class="about-content">
                <h1>The Studio</h1>
                <div class="about-text">
                    <p><strong>Jared Alon</strong> is a Hudson Valley-based design and woodworking studio specializing in heirloom-quality, sculptural furniture. Founded on the principles of material integrity, structural clarity, and meticulous attention to detail, each piece is engineered and crafted by hand.</p>
                    <p>Our philosophy is centered on the relationship between materials. We combine select domestic hardwoods—primarily Walnut, Oak, and Maple—with tactile, organic elements such as vegetable-tanned leather, cork, and wool bouclé. By balancing geometric profiles with soft, hand-shaped details, we create furniture that feels structurally robust yet sculptural and light.</p>
                    <p>Every joint, mortise, and tenon is made to endure generations, prioritizing sustainable craft and local sourcing above all.</p>
                </div>
                
                <div class="contact-block" id="contact">
                    <h3>Contact & Inquiries</h3>
                    <div class="contact-info-grid">
                        <div class="contact-item">
                            <h4>Studio Address</h4>
                            <p>Beacon, New York</p>
                        </div>
                        <div class="contact-item">
                            <h4>General Inquiries</h4>
                            <p>studio@jaredalon.com</p>
                        </div>
                        <div class="contact-item">
                            <h4>Instagram</h4>
                            <p>@jaredalon.design</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """
    
    rendered = render_base("About", content, active_tab="about")
    with open(os.path.join(OUTPUT_DIR, 'about.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)
    print("Built about.html")

def main():
    print("Starting static site build...")
    projects = load_projects()
    print(f"Loaded {len(projects)} projects.")
    
    build_index(projects)
    build_projects_list(projects)
    build_project_details(projects)
    build_gallery(projects)
    build_about()
    
    print("Static site build completed successfully!")

if __name__ == '__main__':
    main()
