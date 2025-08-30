// @ts-nocheck
"use client"

import React, { useState, useRef, useEffect, Suspense } from "react"
import dynamic from "next/dynamic"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { cn } from "@/lib/utils"
import { Info, AlertTriangle, CheckCircle2, Loader2, Sparkles, Download, BookOpen, CircleDot, Copy, Wand2, FileText, Bot, FileUp, FilePlus, Menu, X, RotateCw, ArrowLeft } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeRaw from "rehype-raw"
// @ts-ignore
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
// @ts-ignore
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism"
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from "@/components/ui/resizable"


type GenerationStep = "idle" | "styling" | "styling_complete" | "planning" | "writing" | "assembling" | "complete" | "error"
type UiStep = 'style' | 'content' | 'results'

type StepStatus = "pending" | "processing" | "completed" | "error"

interface Plan {
  section_title: string
  goal: string
  relevant_code_snippets: string[]
}

const StatusIndicator: React.FC<{ status: StepStatus; label: string }> = ({ status, label }) => {
  const statusConfig = {
    pending: {
      icon: <CircleDot className="h-4 w-4" />,
      text: "Pending",
      className: "bg-muted text-muted-foreground",
    },
    processing: {
      icon: <Loader2 className="h-4 w-4 animate-spin" />,
      text: "Processing",
      className: "bg-accent text-accent-foreground",
    },
    completed: {
      icon: <CheckCircle2 className="h-4 w-4" />,
      text: "Completed",
      className: "bg-secondary text-secondary-foreground",
    },
    error: {
      icon: <AlertTriangle className="h-4 w-4" />,
      text: "Error",
      className: "bg-destructive text-destructive-foreground",
    },
  }

  const { icon, text, className } = statusConfig[status]

  return (
    <div aria-label={`${label}: ${text}`} role="status" className={cn("flex items-center gap-2 text-sm font-medium px-3 py-1.5 rounded-md w-full", className)}>
      {icon}
      <span className="font-semibold">{label}</span>
    </div>
  )
}

export function CookbookGenerator() {
  const [uiStep, setUiStep] = useState<UiStep>('style')
  const [sourceCode, setSourceCode] = useState("")
  const [userGuidance, setUserGuidance] = useState("")
  const [exampleCookbook, setExampleCookbook] = useState("")
  const [currentStep, setCurrentStep] = useState<GenerationStep>("idle")
  const [error, setError] = useState<string | null>(null)
  
  const [styleJson, setStyleJson] = useState<Record<string, any> | null>(null)
  const [plan, setPlan] = useState<Plan[] | null>(null)
  const [writingProgress, setWritingProgress] = useState(0)
  // Track detailed writing progress so we can show which section is being processed
  const [progressMessage, setProgressMessage] = useState<string>("")
  const [currentSection, setCurrentSection] = useState<number | null>(null)
  const [totalSections, setTotalSections] = useState<number | null>(null)
  const [draftedContent, setDraftedContent] = useState<string[]>([])
  const [finalCookbook, setFinalCookbook] = useState<string | null>(null)
  
  const abortControllerRef = useRef<AbortController | null>(null)
  const { toast } = useToast()
  const contentRef = useRef<HTMLDivElement | null>(null)
  const resultsRef = useRef<HTMLDivElement | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const MIN_EXAMPLE_LEN = 200
  const MIN_GUIDANCE_LEN = 50
  const [infoOpen, setInfoOpen] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [showFullCookbook, setShowFullCookbook] = useState(false)

  useEffect(() => {
    if (uiStep === 'content') {
      contentRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    if (uiStep === 'results') {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [uiStep])

  const handleAnalyzeStyle = async () => {
    if (!exampleCookbook.trim() || !userGuidance.trim()) {
      setError("Please provide both an example cookbook and user guidance to analyze the style.")
      return
    }
    
    if (abortControllerRef.current) abortControllerRef.current.abort()
    
    setError(null)
    setStyleJson(null)
    setCurrentStep("styling")

    const abortController = new AbortController()
    abortControllerRef.current = abortController

    try {
      const response = await fetch("http://127.0.0.1:8080/api/generate-cookbook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_guidance: userGuidance,
          example_cookbook: exampleCookbook,
        }),
        signal: abortController.signal,
      })

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      if (!reader) throw new Error("No response body")

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          
          try {
            const data = JSON.parse(line.slice(6))
            if (data.error) {
                setError(data.error)
                setCurrentStep("error")
                return
            }
            if (data.status === 'styling_complete') {
              setStyleJson(data.style_json)
              setCurrentStep('styling_complete')
              abortControllerRef.current?.abort() // Stop the stream
              return // Exit the loop
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, line)
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(err.message || "An error occurred during style analysis.")
        setCurrentStep("error")
      }
    } finally {
      abortControllerRef.current = null
    }
  }

  const handleGenerateCookbook = async () => {
    if (!sourceCode.trim() || !styleJson) {
      setError("Source code is missing or style has not been analyzed.")
      return
    }

    if (abortControllerRef.current) abortControllerRef.current.abort()

    setError(null)
    setPlan(null)
    setDraftedContent([])
    setFinalCookbook(null)
    setWritingProgress(0)
    setCurrentStep("planning")
    setUiStep("results")

    const abortController = new AbortController()
    abortControllerRef.current = abortController

    try {
      const response = await fetch("http://127.0.0.1:8080/api/generate-cookbook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_code: sourceCode,
          user_guidance: userGuidance,
          style_json: styleJson,
        }),
        signal: abortController.signal,
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      if (!reader) throw new Error("No response body")

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.error) {
              setError(data.error)
              setCurrentStep("error")
              return
            }

            switch (data.status) {
              case 'planning': setCurrentStep('planning'); break
              case 'planning_complete': setPlan(data.plan); setCurrentStep('writing'); break
              case 'writing':
                setCurrentStep('writing')
                // Save progress metrics and message for UI display
                if (typeof data.total_sections === 'number') setTotalSections(data.total_sections)
                if (typeof data.section_number === 'number') setCurrentSection(data.section_number)
                if (data.section_number && data.total_sections) {
                  setWritingProgress((data.section_number / data.total_sections) * 100)
                }
                if (data.message) setProgressMessage(data.message)
                break
              case 'writing_complete': setDraftedContent(data.drafted_content); setWritingProgress(100); setCurrentStep('assembling'); break
              case 'assembling':
                setCurrentStep('assembling');
                if (data.message) setProgressMessage(data.message)
                 break
              case 'complete': 
                setFinalCookbook(data.final_cookbook); 
                setCurrentStep('complete'); 
                break
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, line)
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(err.message || "An error occurred while generating the cookbook.")
        setCurrentStep("error")
      }
    } finally {
      abortControllerRef.current = null
    }
  }

  const handleDownloadCookbook = () => {
    if (!finalCookbook) return
    const blob = new Blob([finalCookbook], { type: "text/markdown;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = "cookbook.mdx"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    toast({ title: "Download started", description: "Your cookbook is downloading." })
  }

  const handleCopyCookbook = () => {
    if (!finalCookbook) return
    navigator.clipboard.writeText(finalCookbook)
    toast({ title: "Copied", description: "Cookbook copied to clipboard" })
  }
  
  const getStepStatus = (step: GenerationStep): StepStatus => {
    if (currentStep === "error") return "error"
    if (step === currentStep) return "processing"
    
    const steps: GenerationStep[] = ["styling", "planning", "writing", "assembling", "complete"]
    const currentIndex = steps.indexOf(currentStep as any)
    const stepIndex = steps.indexOf(step)

    if (currentStep === 'styling_complete' && step === 'styling') return 'completed'
    if (stepIndex < currentIndex) return "completed"
    
    return "pending"
  }
  
  const resetAll = () => {
      if (abortControllerRef.current) abortControllerRef.current.abort()
      setUiStep('style')
      setCurrentStep('idle')
      setError(null)
      setStyleJson(null)
      setPlan(null)
      setDraftedContent([])
      setFinalCookbook(null)
      setWritingProgress(0)
      setProgressMessage("")
      setCurrentSection(null)
      setTotalSections(null)
  }

  const loadSampleCookbook = () => {
    const sample = "# Sample Cookbook\n\nThis is a short sample demonstrating style.";
    setExampleCookbook(sample)
    toast({ title: "Sample loaded" })
  }
  const triggerFileSelect = () => {
    fileInputRef.current?.click()
  }
  const handleFileChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      const text = ev.target?.result as string
      setExampleCookbook(text)
      toast({ title: "File loaded", description: file.name })
    }
    reader.readAsText(file)
  }

  const StyleStep = () => (
    <Card ref={contentRef}
      className="space-y-6 shadow-md"
      onDragOver={(e) => {
        e.preventDefault();
      }}
      onDrop={(e) => {
        e.preventDefault();
        const file = e.dataTransfer.files?.[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (ev) => {
            setExampleCookbook(ev.target?.result as string);
            toast({ title: "File loaded", description: file.name });
          };
          reader.readAsText(file);
        }
      }}
    >
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Wand2 /> 1. Define Style & Intent <span className="text-sm font-normal text-muted-foreground">(Step 1 of 3)</span></CardTitle>
      </CardHeader>
      <CardContent className="p-8 space-y-6">
        <div className="space-y-2">
          <label htmlFor="example-cookbook" className="font-medium">Example Cookbook (for Style)</label>
          <Textarea id="example-cookbook" value={exampleCookbook} onChange={(e) => setExampleCookbook(e.target.value)} className="h-48" placeholder="Paste an example of a cookbook or technical document that has the style, tone, and structure you want to emulate..." />
          <p className={`text-xs ${exampleCookbook.length < MIN_EXAMPLE_LEN ? 'text-destructive' : 'text-muted-foreground'}`}>{exampleCookbook.length} / {MIN_EXAMPLE_LEN}+ characters</p>
          <div className="flex gap-3">
            <Button type="button" size="sm" variant="secondary" onClick={loadSampleCookbook}><FilePlus className="h-4 w-4"/>Load Sample</Button>
            <Button aria-label="Upload a cookbook file" type="button" size="sm" variant="outline" onClick={triggerFileSelect}><FileUp className="h-4 w-4"/>Upload File</Button>
            <input aria-label="File input" type="file" accept=".md,.txt,.mdx" ref={fileInputRef} onChange={handleFileChange} className="hidden" />
          </div>
        </div>
        <div className="space-y-2">
          <label htmlFor="user-guidance" className="font-medium">User Guidance</label>
          <Textarea id="user-guidance" value={userGuidance} onChange={(e) => setUserGuidance(e.target.value)} className="h-32" placeholder="Describe your cookbook's goals, target audience, and any specific instructions..." />
          <p className={`text-xs ${userGuidance.length < MIN_GUIDANCE_LEN ? 'text-destructive' : 'text-muted-foreground'}`}>{userGuidance.length} / {MIN_GUIDANCE_LEN}+ characters</p>
        </div>
      </CardContent>
      <CardFooter className="flex pt-4">
        <Button size="lg" className="w-full" onClick={handleAnalyzeStyle} disabled={currentStep === 'styling' || exampleCookbook.length < MIN_EXAMPLE_LEN || userGuidance.length < MIN_GUIDANCE_LEN}>
            {currentStep === 'styling' ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analyzing...</> : 'Analyze Style'}
        </Button>
      </CardFooter>
    </Card>
  )

  const StyleAnalysisResult = () => (
    <Card className="border-border bg-primary/10 shadow-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-primary"><Sparkles className="h-5 w-5" />Style Analysis Complete</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <Accordion type="single" collapsible defaultValue="summary">
          <AccordionItem value="summary">
            <AccordionTrigger>View Style Summary</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 text-sm p-4 md:p-6 bg-card rounded-lg border">
                {styleJson && (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
                      <div><strong className="font-semibold text-primary block">Title:</strong> {styleJson.cookbook_metadata?.title || 'N/A'}</div>
                      <div><strong className="font-semibold text-primary block">Difficulty:</strong> {styleJson.cookbook_metadata?.difficulty_level || 'N/A'}</div>
                      <div><strong className="font-semibold text-primary block">Tone:</strong> {styleJson.writing_style?.tone || 'N/A'}</div>
                      <div><strong className="font-semibold text-primary block">Formality:</strong> {styleJson.writing_style?.formality_level || 'N/A'}/10</div>
                      <div><strong className="font-semibold text-primary block">Tech Depth:</strong> {styleJson.writing_style?.technical_depth || 'N/A'}</div>
                      <div><strong className="font-semibold text-primary block">Audience:</strong> {styleJson.cookbook_metadata?.target_audience || 'N/A'}</div>
                    </div>
                    <div className="pt-4 mt-4 border-t border-border">
                      <strong className="font-semibold text-primary block">Description:</strong>
                      <p className="text-muted-foreground mt-1">{styleJson.cookbook_metadata?.description || 'N/A'}</p>
                    </div>
                  </>
                )}
              </div>
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="full-json">
            <AccordionTrigger>View Full Style JSON</AccordionTrigger>
            <AccordionContent>
              <div className="bg-popover rounded-md p-4 overflow-x-auto">
                <pre className="text-secondary text-sm"><code>{styleJson ? JSON.stringify(styleJson, null, 2) : ''}</code></pre>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
      <CardFooter>
        <Button size="lg" onClick={() => setUiStep('content')} className="w-full">
            Next: Add Source Code
        </Button>
      </CardFooter>
    </Card>
  )

  const ContentStep = () => (
    <Card ref={contentRef} className="shadow-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><FileText /> 2. Provide Source Code <span className="text-sm font-normal text-muted-foreground">(Step 2 of 3)</span></CardTitle>
      </CardHeader>
      <CardContent className="p-8 space-y-6">
        <div className="space-y-2">
            <label htmlFor="source-code" className="font-medium">Source Code</label>
            <Textarea id="source-code" value={sourceCode} onChange={(e) => setSourceCode(e.target.value)} className="h-64 font-mono text-sm py-2 px-4 focus-visible:ring-2 focus-visible:ring-ring" placeholder="Paste your source code here..." />
            <p className="text-xs text-muted-foreground">{sourceCode.length} characters</p>
        </div>
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>The cookbook will be generated using the style analyzed in the previous step.</AlertDescription>
        </Alert>
      </CardContent>
      <CardFooter className="flex justify-between items-center w-full px-4 md:px-6 py-4">
        <Button variant="secondary" onClick={() => setUiStep('style')}>Back</Button>
        <Button size="lg" onClick={handleGenerateCookbook} disabled={currentStep !== 'styling_complete'}>
            <Bot className="mr-2 h-4 w-4" />Generate Cookbook
        </Button>
      </CardFooter>
    </Card>
  )

  const ResultsDisplay = () => (
    <div className="space-y-8" ref={resultsRef}>
      {/* Live region for screen readers to announce progress */}
      <div className="sr-only" aria-live="polite">
        {currentStep === 'writing' && `Writing ${Math.round(writingProgress)} percent complete`}
        {currentStep === 'assembling' && 'Assembling final cookbook'}
        {currentStep === 'complete' && 'Cookbook generation complete'}
      </div>

      {finalCookbook && !showFullCookbook && (
        <Alert className="border-emerald-500/50 bg-emerald-50 text-emerald-800">
          <CheckCircle2 className="h-4 w-4 !text-emerald-500" />
          <AlertTitle className="font-semibold !text-emerald-600">Cookbook Generated!</AlertTitle>
          <AlertDescription className="flex items-center justify-between">
            Your cookbook is ready to be reviewed and edited.
            <Button onClick={() => setShowFullCookbook(true)} variant="outline" size="sm">
              <BookOpen className="mr-2 h-4 w-4"/>
              View Cookbook
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Progress card – always show while generation is active; appears ABOVE the plan */}
      {!finalCookbook && currentStep !== 'idle' && (
        <Card className="border-border bg-accent/10 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              {progressMessage || 'Generation in Progress...'}
            </CardTitle>
          </CardHeader>
          {/* <CardContent className="p-4 md:p-6">
            <div className="flex items-center gap-4">
              <p className="text-lg font-semibold text-foreground">
                {currentSection && totalSections ? `Section ${currentSection} of ${totalSections}` : 'Progress'}
              </p>
              <Progress value={writingProgress} className="w-full [&>div]:bg-accent transition-all duration-500 ease-in-out" />
            </div>
          </CardContent> */}
        </Card>
      )}

      {plan && (
        <Card className="shadow-md">
            <CardHeader className="p-4 md:p-6"><CardTitle>Cookbook Plan</CardTitle></CardHeader>
            <CardContent className="p-4 md:p-6 prose prose-sm max-w-none prose-p:my-2 prose-hr:my-6">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {plan.map((section, i) => `**${i + 1}. ${section.section_title}**\n\nGoal: ${section.goal}`).join('\n\n---\n\n')}
                </ReactMarkdown>
            </CardContent>
        </Card>
      )}
      {/* {finalCookbook && !showFullCookbook ? (
        <Card className="border-border bg-secondary/10 shadow-md">
            <CardHeader className="p-4 md:p-6"><CardTitle className="text-secondary">Cookbook Ready!</CardTitle></CardHeader>
            <CardContent className="p-4 md:p-6 space-y-4">
                <Button size="lg" onClick={() => setShowFullCookbook(true)} className="w-full"><BookOpen className="mr-2 h-4 w-4"/>Read Cookbook</Button>
                <Button size="lg" onClick={handleDownloadCookbook} className="w-full"><Download className="mr-2 h-4 w-4"/>Download</Button>
                <Button size="lg" onClick={handleCopyCookbook} className="w-full" variant="secondary"><Copy className="mr-2 h-4 w-4"/>Copy to Clipboard</Button>
                <div className="bg-card p-4 rounded-lg border max-h-96 overflow-y-auto">
                    <Suspense fallback={<Skeleton className="h-40 w-full" />}> 
                      
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={{code({node, inline, className, children, ...props}) { const match = /language-(\w+)/.exec(className || ""); return !inline && match ? ( <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" {...props}>{String(children).replace(/\n$/, "")}</SyntaxHighlighter>) : ( <code className={className} {...props}>{children}</code>)}}} >{finalCookbook}</ReactMarkdown>
                    </Suspense>
                </div>
            </CardContent>
        </Card>
      ) : null} */}
    </div>
  )

  const SidebarContent = () => {
    return (
    <>
      <div className="px-6">
        <h1 className="text-xl font-semibold text-foreground">ACI.DEV Cookbook Generator</h1>
      </div>
      
      {currentStep !== 'idle' && (
        <div className="flex flex-col gap-3 px-4 py-6">
          <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wider px-2">Status</p>
          <StatusIndicator label="Style Analysis" status={getStepStatus("styling")} />
          <StatusIndicator label="Plan Creation" status={getStepStatus("planning")} />
          <StatusIndicator label="Content Writing" status={getStepStatus("writing")} />
          <StatusIndicator label="Final Assembly" status={getStepStatus("assembling")} />
        </div>
      )}

      <div className="mt-auto p-4 space-y-2">
        {/* <ThemeSwitcher /> */}

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button aria-label="About this tool" variant="ghost" className="w-full justify-start gap-2" onClick={() => setInfoOpen(true)}>
                <Info className="h-4 w-4"/> About this tool
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">About this Cookbook Generator</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        {currentStep !== 'idle' && (
          <Button variant="ghost" size="sm" onClick={resetAll} className="w-full justify-start gap-2">
            <RotateCw className="h-4 w-4" /> Start Over
          </Button>
        )}
      </div>
    </>
  )};


  return (
    <div className="bg-background text-foreground min-h-screen">
      <aside className={cn(
        "fixed top-0 left-0 z-50 w-72 h-screen border-r border-border bg-sidebar",
        "flex flex-col py-6 transition-transform duration-300 ease-in-out",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full",
        "md:translate-x-0"
      )}>
        <button 
          onClick={() => setIsSidebarOpen(false)} 
          className="absolute top-4 right-4 p-2 rounded-full md:hidden hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring"
          aria-label="Close sidebar"
        >
          <X className="h-5 w-5" />
        </button>
        <SidebarContent />
      </aside>

      <div className="md:pl-72">
        <header className={cn(
          "fixed top-0 left-0 right-0 z-40 backdrop-blur-sm",
          "flex items-center justify-between p-4 border-b border-border",
          "md:hidden"
        )}>
          <button onClick={() => setIsSidebarOpen(true)} aria-label="Open sidebar" className="p-2 rounded-full hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring">
            <Menu className="h-5 w-5" />
          </button>
          <h1 className="text-lg font-semibold">Cookbook Generator</h1>
        </header>

        <main className={cn(
          showFullCookbook
            ? "h-screen pt-16 md:pt-0"
            : "p-4 pt-20 md:p-8 md:pt-8"
        )}>
         {showFullCookbook && finalCookbook ? (
            <CookbookEditorView
              initialContent={finalCookbook}
              onClose={() => setShowFullCookbook(false)}
            />
          ) : (
          <div className="max-w-7xl mx-auto space-y-8">
            {error && <Alert variant="destructive" className="mb-4"><AlertTriangle className="h-4 w-4" /><AlertTitle>Error</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>}

            {uiStep === 'style' && !styleJson && currentStep !== 'styling' && <StyleStep />}
            {uiStep === 'style' && currentStep === 'styling' && (
              <Card className="flex flex-col items-center justify-center p-8 md:p-12 space-y-4 shadow-md text-center">
                <Wand2 className="h-12 w-12 text-primary" />
                <CardTitle className="text-2xl">Analyzing Style & Intent</CardTitle>
                <p className="text-muted-foreground max-w-md">
                  The AI is reverse-engineering the style, tone, and structure from your example cookbook and guidance. This will create a style guide for generating your new cookbook.
                </p>
                <div className="pt-4">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              </Card>
            )}
            {uiStep === 'style' && styleJson && <StyleAnalysisResult />}
            {uiStep === 'content' && <ContentStep />}
            {uiStep === 'results' && (
              <ResultsDisplay />
            )}
          </div>
          )}
        </main>
      </div>

      <Dialog open={infoOpen} onOpenChange={setInfoOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>About this Cookbook Generator</DialogTitle>
            <DialogDescription>
              Paste an existing cookbook to analyse its style, add your own code, and let the AI craft a polished technical cookbook in minutes.
            </DialogDescription>
          </DialogHeader>
          <p className="text-sm leading-relaxed">
            Steps:<br/>
            1. Provide a style sample & guidance.<br/>
            2. Add your source code.<br/>
            3. Wait while the planner, writer & assembler agents work.<br/>
            4. Download or copy the MDX result.
          </p>
        </DialogContent>
      </Dialog>
    </div>
  )
}


const CookbookEditorView: React.FC<{
  initialContent: string;
  onClose: () => void;
}> = ({ initialContent, onClose }) => {
  const [content, setContent] = useState(initialContent);
  const { toast } = useToast();

  const handleDownload = () => {
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "cookbook.mdx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast({ title: "Download started", description: "Your cookbook is downloading." });
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    toast({ title: "Copied", description: "Cookbook copied to clipboard" });
  };

  return (
    <div className="h-full flex flex-col bg-background">
       <header className="flex items-center justify-between p-2 border-b bg-background/80 backdrop-blur-sm h-16 shrink-0">
        <div className="flex items-center gap-2">
           <Button variant="ghost" size="sm" onClick={onClose}><ArrowLeft className="mr-2 h-4 w-4" />Back to Form</Button>
        </div>
        <h2 className="text-lg font-bold">Generated Cookbook</h2>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleDownload}><Download className="mr-2 h-4 w-4" />Download</Button>
          <Button variant="outline" size="sm" onClick={handleCopy}><Copy className="mr-2 h-4 w-4" />Copy</Button>
        </div>
      </header>
      <ResizablePanelGroup direction="horizontal" className="flex-1">
        <ResizablePanel defaultSize={50}>
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="h-full w-full resize-none border-0 rounded-none focus-visible:ring-0 p-4"
              placeholder="Edit your cookbook markdown here..."
            />
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={50}>
          <div className="h-full overflow-y-auto p-4 md:p-6 bg-zinc-900">
            <div className="prose prose-invert prose-lg max-w-none">
                <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeRaw]}
                    components={{
                        code({node, inline, className, children, ...props}) {
                            const match = /language-(\w+)/.exec(className || "");
                            return !inline && match ? (
                                <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" {...props}>
                                    {String(children).replace(/\n$/, "")}
                                </SyntaxHighlighter>
                            ) : (
                                <code className={className} {...props}>
                                    {children}
                                </code>
                            );
                        }
                    }}
                >
                    {content}
                </ReactMarkdown>
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};
