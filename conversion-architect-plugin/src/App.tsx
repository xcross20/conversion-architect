import { framer, CanvasNode, useIsAllowedTo, Text, Stack, Button } from "@framer/plugin"
import { useState, useEffect } from "react"
import "./App.css"

framer.showUI({
  position: "top right",
  width: 320,
  height: 480,
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

type ViewState = "main" | "compile" | "results"

export function App() {
  const selection = useSelection()
  const page = usePage()
  const [view, setView] = useState<ViewState>("main")
  const [status, setStatus] = useState<string>("")
  const [genomeData, setGenomeData] = useState<any>(null)

  const handleCompileGenome = async () => {
    setStatus("Compiling genome...")
    
    try {
      // Get current page structure
      const pageNodes = await framer.getPageNodes()
      
      // Build genome data from page
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
        section_order: pageNodes.map(n => n.type || "unknown"),
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
      // In production, this would call the Conversion Architect API
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
      // Insert genome structure as text
      await framer.addText({
        text: JSON.stringify(genomeData, null, 2),
        name: "Genome Data",
      })
      setStatus("Genome inserted!")
    } catch (error) {
      setStatus(`Error: ${error}`)
    }
  }

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
        
        <Button
          variant="secondary"
          onClick={() => setView("compile")}
        >
          Configure Family
        </Button>
      </Stack>
      
      {status && (
        <Text variant="label" size={1} color={status.includes("Error") ? "red" : "green"}>
          {status}
        </Text>
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
            <Text variant="label" size={0}>Family</Text>
            <Text variant="label" size={1}>portfolio_v1</Text>
          </Stack>
          
          <Stack direction="vertical" gap={2}>
            <Text variant="label" size={0}>Vertical</Text>
            <Text variant="label" size={1}>home_services</Text>
          </Stack>
          
          <Button variant="secondary" onClick={() => setView("main")}>
            Back
          </Button>
        </Stack>
      )}
      
      <Text variant="label" size={0} color="tertiary" padding={{ top: 4 }}>
        Powered by Conversion Architect
      </Text>
    </Stack>
  )
}

// Helper to extract content from a node
function extractNodeContent(node: CanvasNode): Record<string, any> {
  const content: Record<string, any> = {}
  
  if (node.name) content.name = node.name
  if (node.type) content.type = node.type
  if ((node as any).text) content.text = (node as any).text
  if ((node as any).opacity) content.opacity = (node as any).opacity
  if ((node as any).visible !== undefined) content.visible = (node as any).visible
  
  return content
}
