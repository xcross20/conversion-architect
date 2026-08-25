import { framer, CanvasNode, useIsAllowedTo, Text, Stack, Button, TextInput } from "@framer/plugin"
import { useState, useEffect } from "react"
import "./App.css"
import {
  fetchGA4Data,
  fetchGA4Insights,
  GA4AnalyticsData,
  GA4ConversionInsights,
} from "./ga4"

framer.showUI({
  position: "top right",
  width: 360,
  height: 600,
})

function useSelection() {
  const [selection, setSelection] = useState<CanvasNode[]>([])

  useEffect(() => {
    return framer.subscribeToSelection(setSelection)
  }, [])

  return selection
}

function usePage() {
  const [page, setPage] = useState<{ name: string; id: string } | null>(null)

  useEffect(() => {
    framer.getPage().then(setPage)
  }, [])

  return page
}

type ViewState = "main" | "compile" | "results" | "ga4" | "ga4_insights"

export function App() {
  const selection = useSelection()
  const page = usePage()
  const [view, setView] = useState<ViewState>("main")
  const [status, setStatus] = useState<string>("")
  const [genomeData, setGenomeData] = useState<any>(null)

  // GA4 state
  const [ga4PropertyId, setGa4PropertyId] = useState<string>("")
  const [ga4Data, setGa4Data] = useState<GA4AnalyticsData | null>(null)
  const [ga4Insights, setGa4Insights] = useState<GA4ConversionInsights | null>(null)
  const [ga4Loading, setGa4Loading] = useState(false)

  const handleCompileGenome = async () => {
    setStatus("Compiling genome...")

    try {
      const pageNodes = await framer.getPageNodes()

      const genome = {
        genome_id: `genome_${Date.now()}`,
        name: page?.name || "Untitled Page",
        family_id: "portfolio_v1",
        genes: pageNodes.map((node, i) => ({
          gene_id: `gene_${i}`,
          gene_type: "content",
          section: node.type || "unknown",
          name: node.name || `Element ${i}`,
          content: extractNodeContent(node),
        })),
        section_order: pageNodes.map((n) => n.type || "unknown"),
        tracking_config: {
          events: ["page_view"],
        },
        supported_claims: [],
      }

      setGenomeData(genome)
      setStatus("Genome compiled successfully!")
      setView("results")
    } catch (error) {
      setStatus(`Error: ${error}`)
    }
  }

  const handlePublishPreview = async () => {
    setStatus("Publishing preview...")
    try {
      const previewUrl = `https://preview.conversion-architect.dev/${genomeData?.genome_id}`
      setStatus(`Preview: ${previewUrl}`)
    } catch (error) {
      setStatus(`Error: ${error}`)
    }
  }

  const handleInsertGenome = async () => {
    if (!genomeData) return

    setStatus("Inserting genome elements...")
    try {
      await framer.addText({
        text: JSON.stringify(genomeData, null, 2),
        name: "Genome Data",
      })
      setStatus("Genome inserted!")
    } catch (error) {
      setStatus(`Error: ${error}`)
    }
  }

  const handleFetchGA4 = async () => {
    setGa4Loading(true)
    setStatus("Fetching GA4 data...")
    try {
      const data = await fetchGA4Data(ga4PropertyId || undefined)
      setGa4Data(data)
      setStatus(data ? "GA4 data loaded" : "No GA4 data")
      if (data) setView("ga4")
    } catch (error) {
      setStatus(`Error fetching GA4: ${error}`)
    } finally {
      setGa4Loading(false)
    }
  }

  const handleFetchGA4Insights = async () => {
    setGa4Loading(true)
    setStatus("Generating GA4 insights...")
    try {
      const insights = await fetchGA4Insights(ga4PropertyId || undefined)
      setGa4Insights(insights)
      setStatus(insights ? "Insights generated" : "No insights")
      if (insights) setView("ga4_insights")
    } catch (error) {
      setStatus(`Error: ${error}`)
    } finally {
      setGa4Loading(false)
    }
  }

  const formatPercent = (val: number): string => `${(val * 100).toFixed(1)}%`
  const formatNumber = (val: number): string =>
    val >= 1000 ? `${(val / 1000).toFixed(1)}k` : `${val}`

  return (
    <Stack direction="vertical" gap={4} padding={6}>
      <Text variant="heading" size={3}>
        Conversion Architect
      </Text>
      <Text variant="label" size={1} color="secondary">
        {page?.name || "No page loaded"}
      </Text>

      <Stack gap={3} direction="vertical" padding={{ top: 4 }}>
        <Text variant="label" size={1}>
          Selected: {selection.length} element(s)
        </Text>

        <Button
          variant="primary"
          onClick={handleCompileGenome}
          disabled={selection.length === 0}
        >
          Compile Genome
        </Button>

        <Button variant="secondary" onClick={() => setView("compile")}>
          Configure Family
        </Button>

        <Button variant="secondary" onClick={() => setView("ga4")}>
          GA4 Analytics
        </Button>
      </Stack>

      {status && (
        <Text
          variant="label"
          size={1}
          color={status.includes("Error") ? "red" : "green"}
        >
          {status}
        </Text>
      )}

      {/* GA4 Panel */}
      {view === "ga4" && (
        <Stack direction="vertical" gap={3} padding={{ top: 4 }}>
          <Text variant="label" size={1} fontWeight="bold">
            GA4 Analytics
          </Text>

          <Stack direction="vertical" gap={2}>
            <Text variant="label" size={0}>
              GA4 Property ID
            </Text>
            <TextInput
              value={ga4PropertyId}
              onChange={(e: any) => setGa4PropertyId(e.target.value)}
              placeholder="properties/123456789"
              disabled={ga4Loading}
            />
          </Stack>

          <Stack gap={2} direction="horizontal">
            <Button
              variant="primary"
              onClick={handleFetchGA4}
              disabled={ga4Loading}
            >
              Fetch Data
            </Button>
            <Button
              variant="secondary"
              onClick={handleFetchGA4Insights}
              disabled={ga4Loading || !ga4Data}
            >
              Get Insights
            </Button>
          </Stack>

          {ga4Data && (
            <Stack direction="vertical" gap={3} padding={{ top: 4 }}>
              {/* Summary metrics */}
              <Stack direction="vertical" gap={1}>
                <Text variant="label" size={1} fontWeight="bold">
                  Last {Math.round(
                    (new Date(ga4Data.date_range[1]).getTime() -
                      new Date(ga4Data.date_range[0]).getTime()) /
                      86400000
                  )}{" "}
                  Days
                </Text>
                <Text variant="label" size={0}>
                  Sessions: {formatNumber(ga4Data.total_sessions)}
                </Text>
                <Text variant="label" size={0}>
                  Conversions: {formatNumber(ga4Data.total_conversions)}
                </Text>
                <Text variant="label" size={0}>
                  CVR: {formatPercent(ga4Data.overall_conversion_rate)}
                </Text>
                <Text variant="label" size={0}>
                  Revenue: ${formatNumber(ga4Data.total_conversion_value)}
                </Text>
                <Text
                  variant="label"
                  size={0}
                  color={ga4Data.conversion_trend === "improving" ? "green" : ga4Data.conversion_trend === "declining" ? "red" : "secondary"}
                >
                  Trend: {ga4Data.conversion_trend}{" "}
                  ({ga4Data.conversion_trend_pct > 0 ? "+" : ""}
                  {ga4Data.conversion_trend_pct.toFixed(1)}%)
                </Text>
              </Stack>

              {/* Top keywords */}
              {ga4Data.top_converting_keywords.length > 0 && (
                <Stack direction="vertical" gap={1}>
                  <Text variant="label" size={1} fontWeight="bold">
                    Top Keywords
                  </Text>
                  {ga4Data.top_converting_keywords.slice(0, 5).map((kw) => (
                    <Text key={kw} variant="label" size={0} color="green">
                      ✓ {kw}
                    </Text>
                  ))}
                </Stack>
              )}

              {/* Underperformers */}
              {ga4Data.keywords_need_optimization.length > 0 && (
                <Stack direction="vertical" gap={1}>
                  <Text variant="label" size={1} fontWeight="bold">
                    Needs Optimization
                  </Text>
                  {ga4Data.keywords_need_optimization.slice(0, 5).map((kw) => (
                    <Text key={kw} variant="label" size={0} color="red">
                      ⚠ {kw}
                    </Text>
                  ))}
                </Stack>
              )}

              {/* Best geo */}
              {ga4Data.best_performing_state && (
                <Stack direction="vertical" gap={1}>
                  <Text variant="label" size={1} fontWeight="bold">
                    Best Geo
                  </Text>
                  <Text variant="label" size={0}>
                    State: {ga4Data.best_performing_state}
                  </Text>
                </Stack>
              )}

              {/* Mobile score */}
              <Stack direction="vertical" gap={1}>
                <Text variant="label" size={1} fontWeight="bold">
                  Mobile Experience
                </Text>
                <Text
                  variant="label"
                  size={0}
                  color={ga4Data.mobile_friendly_score > 0.8 ? "green" : "red"}
                >
                  Score: {(ga4Data.mobile_friendly_score * 100).toFixed(0)}%
                  {ga4Data.mobile_friendly_score < 0.8 && " ⚠ Optimize"}
                </Text>
              </Stack>

              {/* Audience */}
              {ga4Data.audience_insights && (
                <Stack direction="vertical" gap={1}>
                  <Text variant="label" size={1} fontWeight="bold">
                    Audience
                  </Text>
                  {Object.entries(ga4Data.audience_insights.age_brackets)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 2)
                    .map(([age, pct]) => (
                      <Text key={age} variant="label" size={0}>
                        {age}: {formatPercent(pct)}
                      </Text>
                    ))}
                </Stack>
              )}

              <Button variant="secondary" onClick={() => setView("main")}>
                Back
              </Button>
            </Stack>
          )}

          {!ga4Data && !ga4Loading && (
            <Button variant="secondary" onClick={() => setView("main")}>
              Back
            </Button>
          )}
        </Stack>
      )}

      {/* GA4 Insights Panel */}
      {view === "ga4_insights" && ga4Insights && (
        <Stack direction="vertical" gap={3} padding={{ top: 4 }}>
          <Text variant="label" size={1} fontWeight="bold">
            Conversion Insights
          </Text>

          {/* Targets */}
          <Stack direction="vertical" gap={1}>
            <Text variant="label" size={1} fontWeight="bold">
              Targets
            </Text>
            <Text variant="label" size={0}>
              Target CVR: {formatPercent(ga4Insights.target_cvr)}
            </Text>
            <Text variant="label" size={0}>
              Target Bounce: {formatPercent(ga4Insights.target_bounce_rate)}
            </Text>
            <Text variant="label" size={0}>
              Target CTA CTR: {formatPercent(ga4Insights.target_cta_click_rate)}
            </Text>
          </Stack>

          {/* Recommendations */}
          <Stack direction="vertical" gap={2}>
            <Text variant="label" size={1} fontWeight="bold">
              Recommendations ({ga4Insights.recommendations.length})
            </Text>
            {ga4Insights.recommendations.map((rec, i) => (
              <Stack
                key={i}
                direction="vertical"
                gap={1}
                padding={{ top: 2, bottom: 2 }}
              >
                <Text
                  variant="label"
                  size={0}
                  fontWeight="bold"
                  color={
                    rec.priority === "high"
                      ? "red"
                      : rec.priority === "medium"
                      ? "secondary"
                      : "tertiary"
                  }
                >
                  [{rec.priority.toUpperCase()}] {rec.title}
                </Text>
                <Text variant="label" size={0}>
                  {rec.description}
                </Text>
                <Text variant="label" size={0} color="secondary">
                  → {rec.recommended_action}
                </Text>
                <Text variant="label" size={0} color="green">
                  Impact: {rec.expected_impact}
                </Text>
              </Stack>
            ))}
          </Stack>

          {/* Design implications */}
          {ga4Insights.design_implications.length > 0 && (
            <Stack direction="vertical" gap={1}>
              <Text variant="label" size={1} fontWeight="bold">
                Design Implications
              </Text>
              {ga4Insights.design_implications.map((impl, i) => (
                <Text key={i} variant="label" size={0} color="secondary">
                  • {impl}
                </Text>
              ))}
            </Stack>
          )}

          {/* Immediate actions */}
          {ga4Insights.immediate_actions.length > 0 && (
            <Stack direction="vertical" gap={1}>
              <Text variant="label" size={1} fontWeight="bold">
                Immediate Actions
              </Text>
              {ga4Insights.immediate_actions.map((action, i) => (
                <Text key={i} variant="label" size={0}>
                  → {action}
                </Text>
              ))}
            </Stack>
          )}

          <Stack gap={2} direction="horizontal">
            <Button
              variant="secondary"
              onClick={() => setView("ga4")}
            >
              Back to Data
            </Button>
            <Button variant="primary" onClick={() => setView("main")}>
              Done
            </Button>
          </Stack>
        </Stack>
      )}

      {view === "results" && genomeData && (
        <Stack direction="vertical" gap={3} padding={{ top: 4 }}>
          <Text variant="label" size={1} fontWeight="bold">
            Genome Compiled
          </Text>
          <Text variant="label" size={0}>
            Genes: {genomeData.genes.length}
          </Text>
          <Text variant="label" size={0}>
            Sections: {genomeData.section_order.join(", ")}
          </Text>

          <Stack gap={2} direction="horizontal">
            <Button variant="secondary" onClick={handlePublishPreview}>
              Preview
            </Button>
            <Button variant="primary" onClick={handleInsertGenome}>
              Insert
            </Button>
          </Stack>

          <Button variant="secondary" onClick={() => setView("main")}>
            Back
          </Button>
        </Stack>
      )}

      {view === "compile" && (
        <Stack direction="vertical" gap={3} padding={{ top: 4 }}>
          <Text variant="label" size={1} fontWeight="bold">
            Design Family
          </Text>

          <Stack direction="vertical" gap={2}>
            <Text variant="label" size={0}>
              Family
            </Text>
            <Text variant="label" size={1}>
              portfolio_v1
            </Text>
          </Stack>

          <Stack direction="vertical" gap={2}>
            <Text variant="label" size={0}>
              Vertical
            </Text>
            <Text variant="label" size={1}>
              home_services
            </Text>
          </Stack>

          <Button variant="secondary" onClick={() => setView("main")}>
            Back
          </Button>
        </Stack>
      )}

      <Text
        variant="label"
        size={0}
        color="tertiary"
        padding={{ top: 4 }}
      >
        Powered by Conversion Architect + GA4
      </Text>
    </Stack>
  )
}

function extractNodeContent(node: CanvasNode): Record<string, any> {
  const content: Record<string, any> = {}

  if (node.name) content.name = node.name
  if (node.type) content.type = node.type
  if ((node as any).text) content.text = (node as any).text
  if ((node as any).opacity) content.opacity = (node as any).opacity
  if ((node as any).visible !== undefined)
    content.visible = (node as any).visible

  return content
}