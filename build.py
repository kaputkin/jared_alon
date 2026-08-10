#!/usr/bin/env python3
import os
import json
import glob
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, '_templates')
PROJECTS_DIR = os.path.join(BASE_DIR, '_projects')
AVAILABLE_DIR = os.path.join(BASE_DIR, '_available')
OUTPUT_DIR = BASE_DIR
PROJECTS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'projects')
AVAILABLE_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'available')

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
    projects.sort(key=lambda x: (x.get('order') is None, x.get('order', float('inf'))))
    return projects

def load_available():
    items = []
    item_files = glob.glob(os.path.join(AVAILABLE_DIR, '*.json'))
    for file_path in item_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                items.append(data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    items.sort(key=lambda x: (x.get('order') is None, x.get('order', float('inf'))))
    return items

def render_base(title, content, active_tab="", is_subpage=False, header_overlay=False, hero_content=""):
    base_html = load_template('base.html')
    
    # Replace active tab tokens
    tabs = ['projects', 'available', 'about']
    for tab in tabs:
        active_class = "active" if tab == active_tab else ""
        base_html = base_html.replace(f"{{{{nav_active_{tab}}}}}", active_class)
        
    base_html = base_html.replace("{{title}}", title)
    base_html = base_html.replace("{{hero_content}}", hero_content)
    base_html = base_html.replace("{{content}}", content)
    base_html = base_html.replace("{{body_class}}", "page-home" if header_overlay else "")
    base_html = base_html.replace("{{header_class}}", "site-header--overlay" if header_overlay else "")
    
    # Adjust paths for relative resolution
    base_path = "../" if is_subpage else ""
    
    # Perform replacement of absolute paths with relative ones
    replacements = {
        'href="/assets/': f'href="{base_path}assets/',
        'src="/assets/': f'src="{base_path}assets/',
        'data-lightbox="/assets/': f'data-lightbox="{base_path}assets/',
        'href="/index.html': f'href="{base_path}index.html',
        'href="/projects.html': f'href="{base_path}projects.html',
        'href="/gallery.html': f'href="{base_path}gallery.html',
        'href="/about.html': f'href="{base_path}about.html',
        'href="/projects/': f'href="{base_path}projects/',
        'href="/available/': f'href="{base_path}available/',
    }
    
    for abs_path, rel_path in replacements.items():
        base_html = base_html.replace(abs_path, rel_path)
        
    return base_html

def build_index(available_items):
    hero_html = """
    <section class="hero-section">
        <div class="hero-image-container">
            <img src="/assets/images/chain-hero.jpg" alt="Jared Alon Studio" class="hero-image">
        </div>
        <div class="hero-content">
        </div>
    </section>
    """
    
    # Build grid of available items for homepage
    grid_items = []
    for item in available_items:
        grid_items.append(f"""
        <article class="project-card">
            <a href="/available/{item['slug']}.html" class="project-card-image-link">
                <img src="{item['hero_image']}" alt="{item['title']}" class="project-card-image" loading="lazy">
            </a>
            <div class="project-card-info">
                <div>
                    <h3 class="project-card-title">{item['title']}</h3>
                    <span class="project-card-category">{item['price']}</span>
                </div>
                <a href="/available/{item['slug']}.html" class="project-card-link">View Detail</a>
            </div>
        </article>
        """)
        
    featured_html = f"""
    <section class="section-padding">
        <div class="container">
            <div class="section-header">
                <div>
                    <h2 class="section-title">Available Work</h2>
                    <span class="section-subtitle">Current Studio Collection</span>
                </div>
                <a href="/gallery.html" class="btn btn-outline" style="padding: 0.5rem 1.5rem; font-size: 0.8rem;">View All</a>
            </div>
            <div class="projects-grid">
                {"".join(grid_items)}
            </div>
        </div>
    </section>
    """
    
    full_content = featured_html
    rendered = render_base("Home", full_content, active_tab="", header_overlay=True, hero_content=hero_html)
    
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)
    print("Built index.html")

def build_projects_list(projects):
    grid_items = []
    for p in projects:
        grid_items.append(f"""
        <article class="project-card project-card--overlay">
            <a href="/projects/{p['slug']}.html" class="project-card-image-link">
                <img src="{p['hero_image']}" alt="{p['title']}" class="project-card-image" loading="lazy">
                <div class="project-card-overlay">
                    <h3 class="project-card-title">{p['title']}</h3>
                </div>
            </a>
        </article>
        """)
        
    content = f"""
    <section class="section-padding container">
        <div class="section-header">
            <div>
                <h1 class="section-title">Projects</h1>
            </div>
        </div>
        <div class="projects-grid projects-grid--tight">
            {"".join(grid_items)}
        </div>
    </section>
    """
    
    rendered = render_base("Projects", content, active_tab="projects")
    with open(os.path.join(OUTPUT_DIR, 'projects.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)
    print("Built projects.html")

def build_available_list(available_items):
    grid_items = []
    for item in available_items:
        grid_items.append(f"""
        <article class="project-card project-card--overlay">
            <a href="/available/{item['slug']}.html" class="project-card-image-link">
                <img src="{item['hero_image']}" alt="{item['title']}" class="project-card-image" loading="lazy">
                <div class="project-card-overlay">
                    <h3 class="project-card-title">{item['title']}</h3>
                </div>
            </a>
        </article>
        """)
        
    content = f"""
    <section class="section-padding container">
        <div class="section-header">
            <div>
                <h1 class="section-title">Available</h1>
            </div>
        </div>
        <div class="projects-grid projects-grid--tight">
            {"".join(grid_items)}
        </div>
    </section>
    """
    
    rendered = render_base("Available", content, active_tab="available")
    with open(os.path.join(OUTPUT_DIR, 'gallery.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)
    print("Built gallery.html (Available listing)")

def build_project_details(projects):
    os.makedirs(PROJECTS_OUTPUT_DIR, exist_ok=True)
    template = load_template('project.html')
    
    for p in projects:
        # Create minor detail images HTML
        detail_images_html = ""
        detail_images = p.get('images', [])[1:] if len(p.get('images', [])) > 1 else []
        for img_path in detail_images:
            detail_images_html += f"""
            <div class="project-detail-img-wrapper">
                <a href="{img_path}" data-lightbox="{img_path}" alt="{p['title']} Detail">
                    <img src="{img_path}" alt="{p['title']} Detail" class="project-detail-img" loading="lazy">
                </a>
            </div>
            """
        
        # Build note HTML if present
        note_html = ""
        if p.get('note'):
            note_html = f'<em style="color: var(--color-text-muted);">{p["note"]}</em>'
            
        # Render project content
        project_content = template
        project_content = project_content.replace("{{title}}", p.get('title', ''))
        project_content = project_content.replace("{{category}}", p.get('category', ''))
        project_content = project_content.replace("{{description}}", p.get('description', ''))
        project_content = project_content.replace("{{note_html}}", note_html)
        project_content = project_content.replace("{{hero_image}}", p.get('hero_image', ''))
        project_content = project_content.replace("{{project_images}}", detail_images_html)
        
        rendered = render_base(p.get('title', ''), project_content, active_tab="projects", is_subpage=True)
        
        out_path = os.path.join(PROJECTS_OUTPUT_DIR, f"{p['slug']}.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print(f"Built projects/{p['slug']}.html")

def build_available_details(available_items):
    os.makedirs(AVAILABLE_OUTPUT_DIR, exist_ok=True)
    template = load_template('available.html')
    
    for item in available_items:
        # Create minor detail images HTML
        detail_images_html = ""
        detail_images = item.get('images', [])[1:] if len(item.get('images', [])) > 1 else []
        for img_path in detail_images:
            detail_images_html += f"""
            <div class="project-detail-img-wrapper">
                <a href="{img_path}" data-lightbox="{img_path}" alt="{item['title']} Detail">
                    <img src="{img_path}" alt="{item['title']} Detail" class="project-detail-img" loading="lazy">
                </a>
            </div>
            """
        
        # Build notes HTML if present
        notes_html = ""
        if item.get('notes'):
            notes_html = f'<p style="font-style: italic;">{item["notes"]}</p>'
        
        # Render available content
        item_content = template
        item_content = item_content.replace("{{title}}", item.get('title', ''))
        item_content = item_content.replace("{{description}}", item.get('description', ''))
        item_content = item_content.replace("{{notes_html}}", notes_html)
        item_content = item_content.replace("{{dimensions}}", item.get('dimensions', ''))
        item_content = item_content.replace("{{price}}", item.get('price', ''))
        item_content = item_content.replace("{{hero_image}}", item.get('hero_image', ''))
        item_content = item_content.replace("{{available_images}}", detail_images_html)
        
        rendered = render_base(item.get('title', ''), item_content, active_tab="available", is_subpage=True)
        
        out_path = os.path.join(AVAILABLE_OUTPUT_DIR, f"{item['slug']}.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print(f"Built available/{item['slug']}.html")

def build_about():
    content = """
    <section class="about-section container">
        <div class="about-grid">
            <div class="about-image-wrapper">
                <img src="/assets/images/jared.png" alt="Jared Alon Studio" class="about-image">
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
    available_items = load_available()
    print(f"Loaded {len(projects)} projects and {len(available_items)} available items.")
    
    build_index(available_items)
    build_projects_list(projects)
    build_project_details(projects)
    build_available_list(available_items)
    build_available_details(available_items)
    build_about()
    
    print("Static site build completed successfully!")

if __name__ == '__main__':
    main()