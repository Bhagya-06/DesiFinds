import { useState, useEffect, useRef } from "react";
import { useLocation } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, AlertCircle, Loader2, Key, HelpCircle, Heart, Trash2 } from "lucide-react";
import { useChatAssistant } from "@workspace/api-client-react";
import type { ChatMessage, Product } from "@workspace/api-client-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ProductCard from "@/components/ProductCard";
import { getApiKey, setApiKey } from "@/lib/utils";

export default function AIAssistantPage() {
  const [, navigate] = useLocation();
  const [inputMessage, setInputMessage] = useState("");
  const [apiKey, setApiKeyState] = useState(getApiKey);
  const [showApiKey, setShowApiKey] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = localStorage.getItem("desifinds_chat_history");
    return saved ? JSON.parse(saved) : [
      {
        role: "assistant",
        content: "Namaste! I am your DesiFinds AI shopping assistant. Ask me anything about premium Indian alternatives, brands, prices, materials, or features!"
      }
    ];
  });
  const [retrievedProducts, setRetrievedProducts] = useState<Product[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { mutate: sendMessage, isPending, error } = useChatAssistant({
    mutation: {
      onSuccess: (data) => {
        const newMsg: ChatMessage = {
          role: "assistant",
          content: data.response
        };
        const updated = [...messages, newMsg];
        setMessages(updated);
        localStorage.setItem("desifinds_chat_history", JSON.stringify(updated));
        
        if (data.retrievedProducts) {
          setRetrievedProducts(data.retrievedProducts);
        }
      }
    }
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isPending]);

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputMessage.trim()) return;
    
    const userMsg: ChatMessage = {
      role: "user",
      content: inputMessage.trim()
    };
    
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    localStorage.setItem("desifinds_chat_history", JSON.stringify(updatedMessages));
    
    sendMessage({
      data: {
        message: inputMessage.trim(),
        history: messages,
        apiKey: apiKey || undefined
      }
    });
    
    setInputMessage("");
  };

  const handleClearChat = () => {
    const initial = [
      {
        role: "assistant",
        content: "Chat cleared. Ask me about premium Indian alternatives to brands like Zara, Apple, or CeraVe!"
      }
    ];
    setMessages(initial);
    localStorage.setItem("desifinds_chat_history", JSON.stringify(initial));
    setRetrievedProducts([]);
  };

  const suggestions = [
    "What is a premium Indian alternative for Zara Linen Shirt?",
    "Suggest some high quality earbuds like AirPods Pro from boAt or Noise.",
    "Which Indian brand offers skincare products similar to CeraVe?",
    "Suggest premium leather bags from DailyObjects or Mokobara."
  ];

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-6 h-[calc(100vh-4rem)] overflow-hidden">
        {/* Chat area */}
        <div className="flex-1 flex flex-col bg-card border border-card-border rounded-2xl overflow-hidden h-full">
          {/* Header */}
          <div className="p-4 border-b border-border/60 flex items-center justify-between bg-muted/30">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              <div>
                <h1 className="font-semibold text-foreground text-sm">DesiFinds AI Assistant</h1>
                <p className="text-xs text-muted-foreground">Powered by Enterprise RAG & ChromaDB</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowApiKey(!showApiKey)}
                className="p-1.5 rounded-lg border border-border text-muted-foreground hover:text-foreground transition-colors"
                title="OpenAI API Key"
              >
                <Key className="w-4 h-4" />
              </button>
              <button
                onClick={handleClearChat}
                className="p-1.5 rounded-lg border border-border text-muted-foreground hover:text-destructive hover:border-destructive/30 transition-colors"
                title="Clear Chat"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* API Key Panel */}
          <AnimatePresence>
            {showApiKey && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="border-b border-border bg-muted/20 p-4 overflow-hidden"
              >
                <label className="block text-xs font-semibold text-muted-foreground mb-1.5 uppercase tracking-wider">
                  OpenAI API Key (Stored locally)
                </label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => {
                      setApiKeyState(e.target.value);
                      setApiKey(e.target.value);
                    }}
                    placeholder="sk-..."
                    className="flex-1 px-3 py-1.5 border border-border rounded-lg bg-card text-xs outline-none focus:border-primary"
                  />
                  <button
                    onClick={() => setShowApiKey(false)}
                    className="px-3 py-1.5 bg-primary text-primary-foreground text-xs font-semibold rounded-lg"
                  >
                    Save
                  </button>
                </div>
                <p className="text-[10px] text-muted-foreground mt-1.5">
                  Your API key is only used to compute product embeddings and generate responses. It is never stored on our servers.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Messages body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-2xs border ${
                    msg.role === "user"
                      ? "bg-secondary text-secondary-foreground border-secondary-border"
                      : "bg-muted text-foreground border-border"
                  }`}
                >
                  {msg.content.split("\n").map((line, idx) => (
                    <p key={idx} className={idx > 0 ? "mt-2" : ""}>
                      {line}
                    </p>
                  ))}
                </div>
              </div>
            ))}
            {isPending && (
              <div className="flex justify-start">
                <div className="bg-muted text-muted-foreground border border-border rounded-2xl px-4 py-3 text-sm flex items-center gap-2 shadow-2xs">
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  <span>Thinking...</span>
                </div>
              </div>
            )}
            {error && (
              <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-xl text-destructive text-xs">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>Failed to get response. Please check your OpenAI API key or network connection.</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions if empty */}
          {messages.length <= 1 && !isPending && (
            <div className="px-4 py-2 bg-muted/20 border-t border-border/40">
              <p className="text-xs font-semibold text-muted-foreground mb-2">Try asking:</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => {
                      setInputMessage(s);
                    }}
                    className="text-left text-xs p-2 rounded-xl border border-border bg-card hover:border-primary hover:text-primary transition-all line-clamp-1"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Chat input footer */}
          <form onSubmit={handleSend} className="p-4 border-t border-border/60 flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask for alternatives, specifications, buying guides..."
              className="flex-1 px-4 py-2.5 border border-border rounded-xl bg-card text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary transition-colors"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isPending}
              className="px-4 py-2.5 bg-primary text-primary-foreground rounded-xl flex items-center justify-center hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Curation Sidebar (RAG matched products) */}
        {retrievedProducts.length > 0 && (
          <div className="w-full md:w-80 shrink-0 bg-card border border-card-border rounded-2xl flex flex-col h-full overflow-hidden">
            <div className="p-4 border-b border-border/60 bg-muted/30 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="font-semibold text-sm">Relevant Alternatives</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {retrievedProducts.map((p) => (
                <div key={p.id} className="relative">
                  <ProductCard product={p} index={0} />
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
