import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowDown, CheckCircle2, Circle, Loader2, Sparkles } from "lucide-react";
import { useSearchProducts } from "@workspace/api-client-react";
import type { WorkflowStep } from "@workspace/api-client-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import SearchBar from "@/components/SearchBar";
import { getApiKey } from "@/lib/utils";
import { cn } from "@/lib/utils";

const WORKFLOW_NODES = [
  { name: "Product Deconstructor", icon: "🔍", description: "Analyzes the input product to extract category, features, materials, price range, and aesthetic style." },
  { name: "RAG Matcher", icon: "🎯", description: "Queries the Indian products database using semantic search to retrieve the most relevant alternatives." },
  { name: "Review Analyzer", icon: "📊", description: "Analyzes customer reviews and compiles structured lists of pros, cons, and feedback summaries." },
  { name: "Quality Curator", icon: "⚖️", description: "Evaluates each match for similarity score, value proposition, and craftsmanship quality." },
  { name: "Formatter", icon: "📋", description: "Structures the final response with rich product data, match scores, and explanations." },
];

function WorkflowNode({ node, step, index, total }: { node: typeof WORKFLOW_NODES[0]; step?: WorkflowStep; index: number; total: number }) {
  const status = step?.status || "pending";

  return (
    <div className="flex flex-col items-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.15 }}
        className={cn(
          "w-full max-w-md rounded-2xl border p-5 transition-all duration-300",
          status === "complete" ? "border-emerald-400 bg-emerald-50 dark:bg-emerald-900/10" :
          status === "running" ? "border-primary bg-primary/5 shadow-lg shadow-primary/10" :
          "border-border bg-card"
        )}
      >
        <div className="flex items-start gap-4">
          {/* Status icon */}
          <div className={cn(
            "w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0",
            status === "complete" ? "bg-emerald-100 dark:bg-emerald-900/30" :
            status === "running" ? "bg-primary/15" : "bg-muted"
          )}>
            {status === "complete" ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> :
             status === "running" ? <Loader2 className="w-5 h-5 text-primary animate-spin" /> :
             node.icon}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-semibold text-foreground text-sm">{node.name}</h3>
              <span className={cn(
                "text-xs px-2 py-0.5 rounded-full font-medium",
                status === "complete" ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" :
                status === "running" ? "bg-primary/15 text-primary" : "bg-muted text-muted-foreground"
              )}>
                {status === "complete" ? "Complete" : status === "running" ? "Processing..." : "Waiting"}
              </span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">{node.description}</p>
            {step?.output && (
              <div className="mt-3 p-3 rounded-xl bg-background border border-border">
                <p className="text-xs text-foreground font-medium mb-1">Output</p>
                <p className="text-xs text-muted-foreground whitespace-pre-wrap">{step.output}</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {index < total - 1 && (
        <div className="flex flex-col items-center py-2">
          <ArrowDown className="w-5 h-5 text-muted-foreground" />
        </div>
      )}
    </div>
  );
}

export default function WorkflowPage() {
  const [query, setQuery] = useState("");
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([]);
  const [hasRun, setHasRun] = useState(false);

  const { mutate: search, isPending } = useSearchProducts({
    mutation: {
      onSuccess: (data) => {
        setWorkflowSteps(data.workflow);
        setHasRun(true);
      },
    },
  });

  const handleSearch = (q: string) => {
    setQuery(q);
    setHasRun(false);
    search({ data: { query: q, apiKey: getApiKey() || undefined } });
  };

  const getStepForNode = (nodeName: string) => workflowSteps.find((s) => s.name === nodeName);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/30 bg-primary/5 text-primary text-sm font-medium mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            LangGraph Workflow Visualizer
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-3">AI Workflow</h1>
          <p className="text-muted-foreground text-sm max-w-md mx-auto">
            Watch our AI pipeline analyze your product query and find the best Indian alternatives step by step.
          </p>
        </div>

        {/* Search */}
        <div className="mb-10">
          <SearchBar onSearch={handleSearch} placeholder="Enter a product to see the AI workflow..." />
        </div>

        {/* User input node */}
        {(hasRun || isPending || query) && (
          <div className="flex flex-col items-center mb-4">
            <div className="w-full max-w-md rounded-2xl border border-secondary/40 bg-secondary/5 p-4 text-center">
              <div className="flex items-center gap-3 justify-center">
                <div className="w-8 h-8 rounded-lg bg-secondary/20 flex items-center justify-center text-sm">👤</div>
                <div className="text-left">
                  <p className="text-xs text-muted-foreground">User Query</p>
                  <p className="font-medium text-foreground text-sm">{query}</p>
                </div>
              </div>
            </div>
            <div className="py-2">
              <ArrowDown className="w-5 h-5 text-muted-foreground" />
            </div>
          </div>
        )}

        {/* Workflow nodes */}
        <div className="space-y-0">
          {WORKFLOW_NODES.map((node, i) => {
            const step = getStepForNode(node.name);
            let status = "pending";
            if (isPending) {
              const completedSoFar = workflowSteps.filter((s) => s.status === "complete").length;
              if (i < completedSoFar) status = "complete";
              else if (i === completedSoFar) status = "running";
            } else if (hasRun) {
              status = step?.status || "complete";
            }

            return (
              <WorkflowNode
                key={node.name}
                node={node}
                step={step}
                index={i}
                total={WORKFLOW_NODES.length}
              />
            );
          })}
        </div>

        {/* Static diagram when not run */}
        {!hasRun && !isPending && !query && (
          <div className="mt-8 text-center p-8 rounded-2xl border border-dashed border-border">
            <p className="text-muted-foreground text-sm">
              Search for a product above to see the AI workflow execute in real time.
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-4">
              {["Zara Linen Shirt", "AirPods Pro", "CeraVe Moisturizer"].map((ex) => (
                <button
                  key={ex}
                  onClick={() => handleSearch(ex)}
                  className="px-3.5 py-1.5 rounded-full border border-border bg-card text-xs text-muted-foreground hover:border-primary hover:text-primary transition-all"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}
