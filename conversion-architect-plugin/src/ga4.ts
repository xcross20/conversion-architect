/**
 * GA4 Analytics Types
 *
 * TypeScript types matching the Python schemas in
 * conversion_architect/schemas/ga4_analytics.py
 */

export type TrafficSource =
  | "organic_search"
  | "paid_search"
  | "direct"
  | "referral"
  | "social"
  | "email"
  | "display"

export type ConversionStatus =
  | "high_performing"
  | "average"
  | "underperforming"
  | "no_data"

export type UrgencyLevel = "none" | "low" | "medium" | "high" | "critical"

export type ConversionGoal =
  | "phone_call"
  | "lead_capture"
  | "appointment"
  | "purchase"
  | "signup"
  | "quote_request"

export interface KeywordPerformance {
  keyword: string
  sessions: number
  conversions: number
  conversion_rate: number
  conversion_value: number
  bounce_rate: number
  avg_session_duration: number
  page_views: number
  source: TrafficSource
  status: ConversionStatus
}

export interface GeographicPerformance {
  state: string
  city: string | null
  zip_code: string | null
  sessions: number
  conversions: number
  conversion_rate: number
  conversion_value: number
  avg_order_value: number
  status: ConversionStatus
}

export interface DevicePerformance {
  device_category: string
  sessions: number
  conversions: number
  conversion_rate: number
  bounce_rate: number
  avg_page_load_time: number
  mobile_friendly: boolean
}

export interface PagePerformance {
  page_path: string
  page_title: string | null
  sessions: number
  engaged_sessions: number
  conversions: number
  conversion_rate: number
  bounce_rate: number
  avg_engagement_time: number
  exits: number
  exit_rate: number
  status: ConversionStatus
}

export interface AudienceInsight {
  age_brackets: Record<string, number>
  gender_split: Record<string, number>
  interests: string[]
  new_vs_returning: Record<string, number>
  avg_pages_per_session: number
  avg_session_duration: number
}

export interface FunnelAnalysis {
  stages: Array<{ name: string; sessions: number; rate: number }>
  overall_conversion_rate: number
  cart_abandonment_rate: number | null
  form_abandonment_rate: number | null
  primary_drop_off_stage: string | null
}

export interface GA4AnalyticsData {
  report_id: string
  property_id: string
  report_date: string
  date_range: [string, string]
  total_sessions: number
  total_conversions: number
  overall_conversion_rate: number
  total_conversion_value: number
  avg_conversion_value: number
  keyword_performance: KeywordPerformance[]
  top_converting_keywords: string[]
  keywords_need_optimization: string[]
  geographic_performance: GeographicPerformance[]
  best_performing_state: string | null
  worst_performing_state: string | null
  page_performance: PagePerformance[]
  best_performing_page: string | null
  device_performance: DevicePerformance[]
  mobile_friendly_score: number
  audience_insights: AudienceInsight | null
  funnel_analysis: FunnelAnalysis | null
  conversion_trend: "improving" | "declining" | "stable"
  conversion_trend_pct: number
  data_confidence: "high" | "medium" | "low"
  last_updated: string
}

export interface GA4InsightRecommendation {
  insight_type: "keyword" | "geo" | "device" | "content" | "trend"
  priority: "high" | "medium" | "low"
  title: string
  description: string
  data_supporting: Record<string, unknown>
  recommended_action: string
  expected_impact: string
  confidence: "high" | "medium" | "low"
}

export interface GA4ConversionInsights {
  insights_id: string
  ga4_report_id: string
  generated_at: string
  recommendations: GA4InsightRecommendation[]
  design_implications: string[]
  immediate_actions: string[]
  short_term_actions: string[]
  long_term_actions: string[]
  target_cvr: number
  target_bounce_rate: number
  target_cta_click_rate: number
}

export interface BusinessConversionContext {
  context_id: string
  campaign_cell_id: string
  vertical: string
  sub_vertical: string | null
  offer: Record<string, unknown>
  offer_headline: string
  offer_value_prop: string
  offer_urgency: UrgencyLevel
  intent_keywords: string[]
  intent_perceptions: string[]
  conversion_goal: ConversionGoal
  click_to_call_number: string | null
  primary_metric: string
  target_metric_value: number | null
  current_metric_value: number | null
  target_states: string[]
  // GA4 enrichment
  ga4_property_id?: string | null
  ga4_report_id?: string | null
  top_converting_keywords?: string[]
  best_performing_state?: string | null
  best_performing_page?: string | null
  mobile_friendly_score?: number
  conversion_trend?: "improving" | "declining" | "stable"
  conversion_trend_pct?: number
  target_cvr?: number | null
  target_bounce_rate?: number | null
  dominant_age_bracket?: string | null
}

/**
 * Fetch GA4 analytics data from Conversion Architect backend.
 *
 * The plugin doesn't talk to the GA4 MCP server directly (which runs as a
 * Python stdio subprocess). Instead it calls the CA backend API that owns
 * the MCP client and proxies requests.
 *
 * Default backend URL points to localhost during development.
 * In production, set VITE_CA_API_URL or use the production URL.
 */
const CA_API_URL =
  (typeof window !== "undefined" &&
    (window as any).CA_API_URL) ||
  // @ts-ignore - Vite injects import.meta.env
  (import.meta.env?.VITE_CA_API_URL as string) ||
  // Default to deployed Railway URL
  "https://ca-api-production-7266.up.railway.app"

export async function fetchGA4Data(
  propertyId?: string,
  days: number = 30
): Promise<GA4AnalyticsData | null> {
  try {
    const params = new URLSearchParams({
      days: String(days),
    })
    if (propertyId) params.set("property_id", propertyId)

    const response = await fetch(
      `${CA_API_URL}/api/v1/ga4/analytics?${params.toString()}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        mode: "cors",
      }
    )

    if (!response.ok) {
      console.error(`GA4 API returned ${response.status}: ${response.statusText}`)
      return mockGA4Data(propertyId || "properties/demo", days)
    }

    return await response.json()
  } catch (error) {
    console.error("GA4 API fetch failed, using mock data:", error)
    return mockGA4Data(propertyId || "properties/demo", days)
  }
}

export async function fetchGA4Insights(
  propertyId?: string,
  days: number = 30
): Promise<GA4ConversionInsights | null> {
  try {
    const params = new URLSearchParams({
      days: String(days),
    })
    if (propertyId) params.set("property_id", propertyId)

    const response = await fetch(
      `${CA_API_URL}/api/v1/ga4/insights?${params.toString()}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        mode: "cors",
      }
    )

    if (!response.ok) {
      console.error(`GA4 Insights API returned ${response.status}`)
      return mockGA4Insights(propertyId || "properties/demo")
    }

    return await response.json()
  } catch (error) {
    console.error("GA4 Insights API fetch failed, using mock data:", error)
    return mockGA4Insights(propertyId || "properties/demo")
  }
}

/**
 * Mock GA4 data for development and testing.
 */
function mockGA4Data(propertyId: string, days: number): GA4AnalyticsData {
  return {
    report_id: `ga4_rpt_${Date.now()}`,
    property_id: propertyId,
    report_date: new Date().toISOString().split("T")[0],
    date_range: [
      new Date(Date.now() - days * 86400000).toISOString().split("T")[0],
      new Date().toISOString().split("T")[0],
    ],
    total_sessions: 15000,
    total_conversions: 525,
    overall_conversion_rate: 0.035,
    total_conversion_value: 26250,
    avg_conversion_value: 50,
    keyword_performance: [
      {
        keyword: "emergency hvac repair",
        sessions: 1234,
        conversions: 52,
        conversion_rate: 0.042,
        conversion_value: 2340,
        bounce_rate: 0.38,
        avg_session_duration: 145.5,
        page_views: 3456,
        source: "paid_search",
        status: "high_performing",
      },
      {
        keyword: "24 hour plumber",
        sessions: 987,
        conversions: 38,
        conversion_rate: 0.039,
        conversion_value: 1710,
        bounce_rate: 0.42,
        avg_session_duration: 128,
        page_views: 2678,
        source: "paid_search",
        status: "high_performing",
      },
      {
        keyword: "ac repair service",
        sessions: 756,
        conversions: 21,
        conversion_rate: 0.028,
        conversion_value: 945,
        bounce_rate: 0.51,
        avg_session_duration: 95,
        page_views: 1890,
        source: "paid_search",
        status: "average",
      },
    ],
    top_converting_keywords: ["emergency hvac repair", "24 hour plumber"],
    keywords_need_optimization: ["hvac maintenance"],
    geographic_performance: [
      {
        state: "TX",
        city: "Houston",
        zip_code: null,
        sessions: 1567,
        conversions: 78,
        conversion_rate: 0.05,
        conversion_value: 3510,
        avg_order_value: 45,
        status: "high_performing",
      },
      {
        state: "CA",
        city: "Los Angeles",
        zip_code: null,
        sessions: 1234,
        conversions: 52,
        conversion_rate: 0.042,
        conversion_value: 2340,
        avg_order_value: 45,
        status: "high_performing",
      },
    ],
    best_performing_state: "TX",
    worst_performing_state: "IL",
    page_performance: [
      {
        page_path: "/emergency-services",
        page_title: "24/7 Emergency Services",
        sessions: 2345,
        engaged_sessions: 1567,
        conversions: 98,
        conversion_rate: 0.042,
        bounce_rate: 0.33,
        avg_engagement_time: 125.5,
        exits: 312,
        exit_rate: 0.13,
        status: "high_performing",
      },
    ],
    best_performing_page: "/emergency-services",
    device_performance: [
      {
        device_category: "mobile",
        sessions: 3456,
        conversions: 112,
        conversion_rate: 0.032,
        bounce_rate: 0.48,
        avg_page_load_time: 3.8,
        mobile_friendly: true,
      },
      {
        device_category: "desktop",
        sessions: 2345,
        conversions: 104,
        conversion_rate: 0.044,
        bounce_rate: 0.32,
        avg_page_load_time: 2.1,
        mobile_friendly: true,
      },
    ],
    mobile_friendly_score: 0.85,
    audience_insights: {
      age_brackets: {
        "18-24": 0.08,
        "25-34": 0.32,
        "35-44": 0.28,
        "45-54": 0.19,
        "55-64": 0.09,
        "65+": 0.04,
      },
      gender_split: { male: 0.58, female: 0.4 },
      interests: ["Home Services", "Contractors"],
      new_vs_returning: { new: 0.65, returning: 0.35 },
      avg_pages_per_session: 3.2,
      avg_session_duration: 115.5,
    },
    funnel_analysis: {
      stages: [
        { name: "page_view", sessions: 1000, rate: 1.0 },
        { name: "engagement", sessions: 680, rate: 0.68 },
        { name: "cta_click", sessions: 245, rate: 0.245 },
        { name: "phone_call", sessions: 45, rate: 0.045 },
      ],
      overall_conversion_rate: 0.045,
      cart_abandonment_rate: null,
      form_abandonment_rate: 0.72,
      primary_drop_off_stage: "cta_click",
    },
    conversion_trend: "improving",
    conversion_trend_pct: 12.5,
    data_confidence: "high",
    last_updated: new Date().toISOString(),
  }
}

function mockGA4Insights(propertyId: string): GA4ConversionInsights {
  return {
    insights_id: `insights_${Date.now()}`,
    ga4_report_id: `ga4_rpt_${Date.now()}`,
    generated_at: new Date().toISOString(),
    recommendations: [
      {
        insight_type: "keyword",
        priority: "high",
        title: "High CVR keyword: emergency hvac repair",
        description:
          "'emergency hvac repair' has 4.2% CVR with 52 conversions",
        data_supporting: {
          keyword: "emergency hvac repair",
          cvr: 0.042,
          sessions: 1234,
        },
        recommended_action:
          "Prioritize 'emergency hvac repair' in headlines and content",
        expected_impact: "Maintain +4.2% CVR",
        confidence: "high",
      },
      {
        insight_type: "geo",
        priority: "high",
        title: "Best performing state: TX",
        description: "TX has the highest conversion rate at 5.0%",
        data_supporting: { state: "TX", cvr: 0.05 },
        recommended_action: "Prioritize TX in geo-targeting",
        expected_impact: "Focus budget on high-CVR geography",
        confidence: "high",
      },
    ],
    design_implications: [
      "Mobile optimization critical (62% mobile traffic)",
      "Emergency urgency messaging improves CVR",
    ],
    immediate_actions: [
      "Audit mobile page load speed",
      "Increase CTA button size for touch",
      "A/B test CTA button color/size",
    ],
    short_term_actions: ["Test new hero messaging"],
    long_term_actions: ["Expand to additional high-CVR states"],
    target_cvr: 0.045,
    target_bounce_rate: 0.35,
    target_cta_click_rate: 0.06,
  }
}