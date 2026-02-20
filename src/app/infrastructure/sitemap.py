"""Sitemap generator"""

from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from src.app.infrastructure.persistence.models import CategoryModel, ProductModel


class SitemapGenerator:
    """Generate sitemap.xml for the application"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.base_url = settings.app_url
    
    async def generate(self) -> str:
        """Generate sitemap XML"""
        urlset = Element(
            'urlset',
            xmlns="http://www.sitemaps.org/schemas/sitemap/0.9",
        )
        
        self._add_url(urlset, "/", priority="1.0", changefreq="daily")
        self._add_url(urlset, "/products", priority="0.9", changefreq="daily")
        self._add_url(urlset, "/categories", priority="0.8", changefreq="weekly")
        
        stmt = select(CategoryModel)
        result = await self.session.execute(stmt)
        categories = result.scalars().all()
        
        for category in categories:
            self._add_url(
                urlset,
                f"/categories/{category.slug}",
                priority="0.7",
                changefreq="weekly",
            )
        
        stmt = select(ProductModel).order_by(ProductModel.created_at.desc()).limit(1000)
        result = await self.session.execute(stmt)
        products = result.scalars().all()
        
        for product in products:
            self._add_url(
                urlset,
                f"/products/{product.id}",
                lastmod=product.created_at,
                priority="0.6",
                changefreq="weekly",
            )
        
        xml_string = tostring(urlset, encoding='unicode', method='xml')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'
    
    def _add_url(
        self,
        urlset: Element,
        path: str,
        lastmod: datetime | None = None,
        priority: str = "0.5",
        changefreq: str = "weekly",
    ) -> None:
        """Add URL to sitemap"""
        url = SubElement(urlset, 'url')
        
        loc = SubElement(url, 'loc')
        loc.text = f"{self.base_url}{path}"
        
        if lastmod:
            lastmod_elem = SubElement(url, 'lastmod')
            lastmod_elem.text = lastmod.strftime('%Y-%m-%d')
        
        changefreq_elem = SubElement(url, 'changefreq')
        changefreq_elem.text = changefreq
        
        priority_elem = SubElement(url, 'priority')
        priority_elem.text = priority
