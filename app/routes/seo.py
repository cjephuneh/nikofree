from flask import Blueprint, Response
from app import db
from app.models.event import Event
from datetime import datetime

bp = Blueprint('seo', __name__)


@bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate dynamic sitemap.xml"""
    base_url = 'https://niko-free.com'
    
    # Static pages
    urls = [
        {
            'loc': f'{base_url}/',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '1.0'
        },
        {
            'loc': f'{base_url}/become-partner',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.8'
        },
        {
            'loc': f'{base_url}/about',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.7'
        },
        {
            'loc': f'{base_url}/this-weekend',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.9'
        },
        {
            'loc': f'{base_url}/calendar',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        }
    ]
    
    # Dynamic event pages - get published and approved events
    events = Event.query.filter_by(
        is_published=True,
        status='approved'
    ).order_by(Event.created_at.desc()).limit(1000).all()
    
    for event in events:
        urls.append({
            'loc': f'{base_url}/event-detail/{event.id}',
            'lastmod': event.updated_at.strftime('%Y-%m-%d') if event.updated_at else event.created_at.strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.7'
        })
    
    # Generate XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    xml += '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
    xml += '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n'
    xml += '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n'
    
    for url in urls:
        xml += '  <url>\n'
        xml += f'    <loc>{url["loc"]}</loc>\n'
        xml += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{url["priority"]}</priority>\n'
        xml += '  </url>\n'
    
    xml += '</urlset>'
    
    return Response(xml, mimetype='application/xml')


@bp.route('/robots.txt', methods=['GET'])
def robots():
    """Generate robots.txt"""
    robots_txt = """User-agent: *
Allow: /

# Sitemap
Sitemap: https://niko-free.com/sitemap.xml

# Disallow admin and dashboard pages
Disallow: /admin-dashboard
Disallow: /partner-dashboard
Disallow: /user-dashboard
Disallow: /api/

# Allow important pages
Allow: /
Allow: /event-detail/
Allow: /become-partner
Allow: /about
Allow: /this-weekend
Allow: /calendar
"""
    return Response(robots_txt, mimetype='text/plain')

