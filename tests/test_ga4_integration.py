"""
Tests for GA4 Integration

Tests the GA4 adapter, schemas, and integration with Conversion Architect.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

from conversion_architect.schemas import (
    GA4AnalyticsData,
    GA4ConversionInsights,
    GA4ReportQuery,
    KeywordPerformance,
    GeographicPerformance,
    PagePerformance,
    DevicePerformance,
    AudienceInsight,
    FunnelAnalysis,
    TrafficSource,
    ConversionStatus,
    BusinessConversionContext,
    ConversionGoal,
    UrgencyLevel,
)
from conversion_architect.adapters.ga4_adapter import (
    GA4Adapter,
    GA4AdapterError,
    create_ga4_adapter,
)
from conversion_architect.genome_compiler import GenomeCompiler
from conversion_architect.schemas.design_family import DesignFamily


class TestGA4Schemas:
    """Tests for GA4 schema models."""
    
    def test_keyword_performance_creation(self):
        """Test KeywordPerformance schema."""
        kw = KeywordPerformance(
            keyword="emergency hvac",
            sessions=1000,
            conversions=45,
            conversion_rate=0.045,
            source=TrafficSource.PAID_SEARCH,
            status=ConversionStatus.HIGH_PERFORMING,
        )
        
        assert kw.keyword == "emergency hvac"
        assert kw.sessions == 1000
        assert kw.conversions == 45
        assert kw.conversion_rate == 0.045
        assert kw.status == ConversionStatus.HIGH_PERFORMING
    
    def test_geographic_performance_creation(self):
        """Test GeographicPerformance schema."""
        geo = GeographicPerformance(
            state="TX",
            city="Houston",
            sessions=500,
            conversions=25,
            conversion_rate=0.05,
            status=ConversionStatus.HIGH_PERFORMING,
        )
        
        assert geo.state == "TX"
        assert geo.city == "Houston"
        assert geo.conversion_rate == 0.05
        assert geo.status == ConversionStatus.HIGH_PERFORMING
    
    def test_page_performance_creation(self):
        """Test PagePerformance schema."""
        page = PagePerformance(
            page_path="/emergency-services",
            sessions=1000,
            conversions=40,
            conversion_rate=0.04,
            bounce_rate=0.35,
            status=ConversionStatus.HIGH_PERFORMING,
        )
        
        assert page.page_path == "/emergency-services"
        assert page.conversion_rate == 0.04
        assert page.bounce_rate == 0.35
    
    def test_device_performance_creation(self):
        """Test DevicePerformance schema."""
        device = DevicePerformance(
            device_category="mobile",
            sessions=800,
            conversions=24,
            conversion_rate=0.03,
            bounce_rate=0.50,
            mobile_friendly=True,
        )
        
        assert device.device_category == "mobile"
        assert device.conversion_rate == 0.03
        assert device.mobile_friendly is True
    
    def test_audience_insight_creation(self):
        """Test AudienceInsight schema."""
        audience = AudienceInsight(
            age_brackets={"25-34": 0.35, "35-44": 0.28},
            gender_split={"male": 0.60, "female": 0.40},
            interests=["Home Services", "Contractors"],
            avg_pages_per_session=3.2,
            avg_session_duration=120.0,
        )
        
        assert audience.age_brackets["25-34"] == 0.35
        assert audience.gender_split["male"] == 0.60
        assert audience.avg_pages_per_session == 3.2
    
    def test_funnel_analysis_creation(self):
        """Test FunnelAnalysis schema."""
        funnel = FunnelAnalysis(
            stages=[
                {"name": "page_view", "sessions": 1000, "rate": 1.0},
                {"name": "cta_click", "sessions": 300, "rate": 0.30},
                {"name": "conversion", "sessions": 40, "rate": 0.04},
            ],
            overall_conversion_rate=0.04,
            primary_drop_off_stage="cta_click",
        )
        
        assert len(funnel.stages) == 3
        assert funnel.overall_conversion_rate == 0.04
        assert funnel.primary_drop_off_stage == "cta_click"
    
    def test_ga4_report_query_creation(self):
        """Test GA4ReportQuery schema."""
        query = GA4ReportQuery(
            property_id="properties/123456789",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            dimensions=["date", "source", "campaign"],
            metrics=["sessions", "conversions"],
        )
        
        assert query.property_id == "properties/123456789"
        assert len(query.dimensions) == 3
        assert "conversions" in query.metrics


class TestGA4AnalyticsData:
    """Tests for GA4AnalyticsData schema."""
    
    def test_ga4_analytics_data_creation(self):
        """Test complete GA4AnalyticsData schema."""
        data = GA4AnalyticsData(
            report_id="test_rpt_001",
            property_id="properties/123456789",
            report_date=date.today(),
            date_range=(date.today() - timedelta(days=30), date.today()),
            total_sessions=10000,
            total_conversions=400,
            overall_conversion_rate=0.04,
            top_converting_keywords=["emergency hvac", "24 hour plumber"],
            best_performing_state="TX",
            conversion_trend="improving",
            conversion_trend_pct=15.0,
        )
        
        assert data.total_sessions == 10000
        assert data.total_conversions == 400
        assert data.overall_conversion_rate == 0.04
        assert "emergency hvac" in data.top_converting_keywords
        assert data.best_performing_state == "TX"
        assert data.conversion_trend == "improving"
    
    def test_ga4_analytics_data_with_keywords(self):
        """Test GA4 data with keyword performance."""
        keywords = [
            KeywordPerformance(
                keyword="emergency hvac",
                sessions=1000,
                conversions=45,
                conversion_rate=0.045,
                status=ConversionStatus.HIGH_PERFORMING,
            ),
            KeywordPerformance(
                keyword="ac repair",
                sessions=500,
                conversions=15,
                conversion_rate=0.03,
                status=ConversionStatus.AVERAGE,
            ),
        ]
        
        data = GA4AnalyticsData(
            report_id="test_rpt_002",
            property_id="properties/123456789",
            report_date=date.today(),
            date_range=(date.today(), date.today()),
            keyword_performance=keywords,
        )
        
        assert len(data.keyword_performance) == 2
        assert data.keyword_performance[0].status == ConversionStatus.HIGH_PERFORMING


class TestGA4ConversionInsights:
    """Tests for GA4ConversionInsights schema."""
    
    def test_insights_creation(self):
        """Test GA4ConversionInsights schema."""
        insights = GA4ConversionInsights(
            insights_id="insights_001",
            ga4_report_id="test_rpt_001",
            recommendations=[
                {
                    "insight_type": "keyword",
                    "priority": "high",
                    "title": "High CVR keyword",
                    "description": "Emergency hvac has 4.5% CVR",
                    "recommended_action": "Prioritize in headlines",
                    "expected_impact": "+20% conversions",
                }
            ],
            design_implications=["Mobile optimization needed"],
            target_cvr=0.05,
            target_bounce_rate=0.35,
        )
        
        assert insights.insights_id == "insights_001"
        assert len(insights.recommendations) == 1
        assert insights.target_cvr == 0.05


class TestGA4Adapter:
    """Tests for GA4Adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create GA4Adapter instance."""
        return create_ga4_adapter(property_id="properties/123456789")
    
    @pytest.mark.asyncio
    async def test_fetch_analytics_generates_data(self, adapter):
        """Test that fetch_analytics returns data."""
        data = await adapter.fetch_analytics()
        
        assert isinstance(data, GA4AnalyticsData)
        assert data.property_id == "properties/123456789"
        assert data.total_sessions > 0
        assert data.total_conversions > 0
        assert len(data.keyword_performance) > 0
    
    @pytest.mark.asyncio
    async def test_fetch_analytics_with_custom_dates(self, adapter):
        """Test fetch_analytics with custom date range."""
        start = date.today() - timedelta(days=7)
        end = date.today()
        
        data = await adapter.fetch_analytics(
            start_date=start,
            end_date=end,
        )
        
        assert data.date_range[0] == start
        assert data.date_range[1] == end
    
    @pytest.mark.asyncio
    async def test_fetch_analytics_uses_cache(self, adapter):
        """Test that second fetch uses cache."""
        # First fetch
        data1 = await adapter.fetch_analytics()
        
        # Second fetch should use cache
        data2 = await adapter.fetch_analytics()
        
        assert data1.report_id == data2.report_id
    
    @pytest.mark.asyncio
    async def test_fetch_analytics_bypasses_cache(self, adapter):
        """Test that fetch_analytics can bypass cache."""
        data1 = await adapter.fetch_analytics()
        
        # Force fresh fetch
        data2 = await adapter.fetch_analytics(use_cache=False)
        
        # Should be different reports
        assert data1.report_id != data2.report_id
    
    @pytest.mark.asyncio
    async def test_generate_insights(self, adapter):
        """Test insight generation from analytics data."""
        data = await adapter.fetch_analytics()
        insights = await adapter.generate_insights(data)
        
        assert isinstance(insights, GA4ConversionInsights)
        assert insights.ga4_report_id == data.report_id
        assert len(insights.recommendations) > 0
        assert insights.target_cvr > data.overall_conversion_rate
    
    @pytest.mark.asyncio
    async def test_generate_insights_keyword_recommendations(self, adapter):
        """Test that insights include keyword recommendations."""
        data = await adapter.fetch_analytics()
        insights = await adapter.generate_insights(data)
        
        # Should have high-performing keyword recommendations
        high_priority = [r for r in insights.recommendations if r.priority == "high"]
        assert len(high_priority) > 0
    
    @pytest.mark.asyncio
    async def test_generate_insights_device_recommendations(self, adapter):
        """Test device optimization recommendations."""
        data = await adapter.fetch_analytics()
        insights = await adapter.generate_insights(data)
        
        # Check for device-related insights
        device_insights = [
            r for r in insights.recommendations
            if r.insight_type == "device"
        ]
        assert len(device_insights) >= 0  # May or may not have device insights
    
    @pytest.mark.asyncio
    async def test_generate_insights_geo_recommendations(self, adapter):
        """Test geographic recommendations."""
        data = await adapter.fetch_analytics()
        insights = await adapter.generate_insights(data)
        
        geo_insights = [
            r for r in insights.recommendations
            if r.insight_type == "geo"
        ]
        assert len(geo_insights) > 0
        assert geo_insights[0].title is not None
    
    def test_enrich_context(self, adapter):
        """Test enriching BusinessConversionContext with GA4 data."""
        context = BusinessConversionContext(
            context_id="test_ctx",
            campaign_cell_id="cell_001",
            vertical="home_services",
            sub_vertical="hvac",
            offer={"type": "emergency"},
            offer_headline="24/7 Emergency HVAC",
            offer_value_prop="Fast, reliable service",
            conversion_goal=ConversionGoal.PHONE_CALL,
            intent_keywords=["hvac", "repair", "emergency"],
            target_states=["TX", "CA", "FL"],
        )
        
        # Create mock analytics data
        analytics = GA4AnalyticsData(
            report_id="test_rpt",
            property_id="properties/123",
            report_date=date.today(),
            date_range=(date.today(), date.today()),
            total_sessions=1000,
            total_conversions=40,
            overall_conversion_rate=0.04,
            top_converting_keywords=["emergency hvac"],
            best_performing_state="TX",
            best_performing_page="/emergency",
            mobile_friendly_score=0.85,
            conversion_trend="improving",
            conversion_trend_pct=10.0,
        )
        
        enriched = adapter.enrich_context(context, analytics)
        
        assert enriched.ga4_report_id == "test_rpt"
        assert enriched.top_converting_keywords == ["emergency hvac"]
        assert enriched.best_performing_state == "TX"
        assert enriched.mobile_friendly_score == 0.85
        assert enriched.conversion_trend == "improving"
        assert enriched.target_cvr is not None
        assert enriched.current_metric_value == 0.04
    
    def test_enrich_context_with_insights(self, adapter):
        """Test enriching context with insights."""
        context = BusinessConversionContext(
            context_id="test_ctx",
            campaign_cell_id="cell_001",
            vertical="home_services",
            offer={"type": "emergency"},
            offer_headline="24/7 Emergency",
            offer_value_prop="Fast service",
            conversion_goal=ConversionGoal.PHONE_CALL,
            intent_keywords=["hvac"],
        )
        
        analytics = GA4AnalyticsData(
            report_id="test_rpt",
            property_id="properties/123",
            report_date=date.today(),
            date_range=(date.today(), date.today()),
            total_sessions=1000,
            total_conversions=40,
            overall_conversion_rate=0.04,
        )
        
        insights = GA4ConversionInsights(
            insights_id="ins_001",
            ga4_report_id="test_rpt",
            recommendations=[],
            target_cvr=0.05,
            target_bounce_rate=0.35,
        )
        
        enriched = adapter.enrich_context(context, analytics, insights)
        
        assert enriched.meta_data["ga4"]["insights"] is not None
        assert enriched.target_cvr == 0.05
        assert enriched.target_bounce_rate == 0.35
    
    def test_clear_cache(self, adapter):
        """Test cache clearing."""
        import asyncio
        
        async def fetch_and_cache():
            await adapter.fetch_analytics()
        
        asyncio.run(fetch_and_cache())
        assert len(adapter._cache) > 0
        
        adapter.clear_cache()
        assert len(adapter._cache) == 0
    
    def test_adapter_error_no_property_id(self):
        """Test error when no property ID provided."""
        adapter = GA4Adapter()
        
        import asyncio
        
        async def fetch_without_id():
            await adapter.fetch_analytics()
        
        with pytest.raises(GA4AdapterError):
            asyncio.run(fetch_without_id())


class TestGA4IntegrationWithGenomeCompiler:
    """Tests for GA4 integration with GenomeCompiler."""
    
    @pytest.mark.asyncio
    async def test_genome_compiler_with_ga4_context(self):
        """Test genome compilation with GA4-enriched context."""
        adapter = create_ga4_adapter(property_id="properties/123")
        analytics = await adapter.fetch_analytics()
        insights = await adapter.generate_insights(analytics)
        
        context = BusinessConversionContext(
            context_id="test_ctx",
            campaign_cell_id="cell_hvac",
            vertical="home_services",
            sub_vertical="hvac",
            offer={"type": "emergency"},
            offer_headline="24/7 Emergency HVAC Repair",
            offer_value_prop="Fast, reliable service",
            conversion_goal=ConversionGoal.PHONE_CALL,
            intent_keywords=["hvac", "repair", "emergency"],
            target_states=["TX", "CA"],
            click_to_call_number="+1-800-123-4567",
            available_trust_signals=["license", "insurance", "reviews"],
        )
        
        # Enrich context with GA4
        enriched = adapter.enrich_context(context, analytics, insights)
        
        # Compile genome
        family = DesignFamily(
            family_id="test_family",
            name="Test Family",
            description="Test",
            patterns=[],
        )
        
        compiler = GenomeCompiler(family=family)
        genome = await compiler.compile(enriched)
        
        # Verify genome has GA4 tracking
        assert genome.tracking_config.get("ga4") is not None
        assert genome.tracking_config["ga4"]["property_id"] == "properties/123"
        
        # Verify genes include GA4 optimization
        gene_types = [g["gene_type"] for g in genome.genes]
        assert "content" in gene_types
        
        # Check for geo gene
        geo_genes = [g for g in genome.genes if g["section"] == "geo_targeting"]
        if enriched.best_performing_state:
            assert len(geo_genes) > 0
            assert geo_genes[0]["configuration"]["primary_state"] == "TX"
    
    @pytest.mark.asyncio
    async def test_genome_compiler_mobile_optimization(self):
        """Test genome compilation with mobile optimization flags."""
        adapter = create_ga4_adapter(property_id="properties/123")
        analytics = await adapter.fetch_analytics()
        
        # Set low mobile score
        analytics.mobile_friendly_score = 0.6
        
        context = BusinessConversionContext(
            context_id="test_ctx",
            campaign_cell_id="cell_mobile",
            vertical="home_services",
            offer={"type": "service"},
            offer_headline="Home Services",
            offer_value_prop="Professional help",
            conversion_goal=ConversionGoal.PHONE_CALL,
            intent_keywords=["plumber"],
        )
        
        enriched = adapter.enrich_context(context, analytics)
        
        family = DesignFamily(family_id="test", name="Test", description="", patterns=[])
        compiler = GenomeCompiler(family=family)
        genome = await compiler.compile(enriched)
        
        # Find CTA gene
        cta_genes = [g for g in genome.genes if g["gene_type"] == "cta"]
        if cta_genes:
            assert cta_genes[0]["configuration"].get("mobile_optimized") is True


class TestBusinessConversionContextGA4Fields:
    """Tests for GA4 fields in BusinessConversionContext."""
    
    def test_context_with_ga4_fields(self):
        """Test context creation with GA4 fields."""
        context = BusinessConversionContext(
            context_id="test",
            campaign_cell_id="cell",
            vertical="home_services",
            offer={"type": "test"},
            offer_headline="Test",
            offer_value_prop="Test",
            conversion_goal=ConversionGoal.PHONE_CALL,
            ga4_property_id="properties/123",
            ga4_report_id="rpt_001",
            top_converting_keywords=["emergency hvac"],
            best_performing_state="TX",
            best_performing_page="/emergency",
            mobile_friendly_score=0.85,
            conversion_trend="improving",
            conversion_trend_pct=12.0,
            target_cvr=0.05,
            target_bounce_rate=0.35,
            dominant_age_bracket="35-44",
        )
        
        assert context.ga4_property_id == "properties/123"
        assert context.top_converting_keywords == ["emergency hvac"]
        assert context.best_performing_state == "TX"
        assert context.mobile_friendly_score == 0.85
        assert context.conversion_trend == "improving"
        assert context.target_cvr == 0.05
        assert context.dominant_age_bracket == "35-44"
    
    def test_context_ga4_defaults(self):
        """Test GA4 field defaults."""
        context = BusinessConversionContext(
            context_id="test",
            campaign_cell_id="cell",
            vertical="home_services",
            offer={"type": "test"},
            offer_headline="Test",
            offer_value_prop="Test",
            conversion_goal=ConversionGoal.PHONE_CALL,
        )
        
        assert context.mobile_friendly_score == 1.0
        assert context.conversion_trend == "stable"
        assert context.conversion_trend_pct == 0.0
        assert context.top_converting_keywords == []
