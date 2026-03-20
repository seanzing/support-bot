import { useState, useCallback, useEffect, useRef } from "react";
import { ChatKitPanel } from "./ChatKitPanel";
import { ThemeToggle } from "./ThemeToggle";
import type { ColorScheme } from "../hooks/useColorScheme";
import { Card } from "@/components/ui/card";
import { MessageCircle, X, ChevronDown, Globe, Zap, Users, Star } from "lucide-react";

// SessionStorage key for tracking dismissed state during this session
const WIDGET_DISMISSED_KEY = "zing-widget-dismissed";

type WidgetDemoProps = {
  scheme: ColorScheme;
  onThemeChange: (scheme: ColorScheme) => void;
  /** Whether to auto-open the widget (default: true) */
  autoOpen?: boolean;
  /** Delay in ms before auto-opening (default: 5000) */
  autoOpenDelay?: number;
};

export function WidgetDemo({
  scheme,
  onThemeChange,
  autoOpen = true,
  autoOpenDelay = 5000,
}: WidgetDemoProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const autoOpenTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Auto-open logic with sessionStorage persistence
  useEffect(() => {
    // Skip if autoOpen is disabled
    if (!autoOpen) return;

    // Check if user already dismissed the widget this session
    const wasDismissed = sessionStorage.getItem(WIDGET_DISMISSED_KEY) === "true";
    if (wasDismissed) return;

    // Set timer to auto-open
    autoOpenTimerRef.current = setTimeout(() => {
      setIsOpen(true);
    }, autoOpenDelay);

    // Cleanup timer on unmount
    return () => {
      if (autoOpenTimerRef.current) {
        clearTimeout(autoOpenTimerRef.current);
      }
    };
  }, [autoOpen, autoOpenDelay]);

  // Handle closing the widget (mark as dismissed for this session)
  const handleClose = useCallback(() => {
    setIsOpen(false);
    // Remember that user dismissed it (only for this session)
    sessionStorage.setItem(WIDGET_DISMISSED_KEY, "true");
    // Clear any pending auto-open timer
    if (autoOpenTimerRef.current) {
      clearTimeout(autoOpenTimerRef.current);
      autoOpenTimerRef.current = null;
    }
  }, []);

  // Handle toggle (only mark as dismissed when closing, not when manually opening)
  const handleToggle = useCallback(() => {
    if (isOpen) {
      handleClose();
    } else {
      setIsOpen(true);
    }
  }, [isOpen, handleClose]);

  const handleThreadChange = useCallback((nextThreadId: string | null) => {
    setThreadId(nextThreadId);
  }, []);

  const handleResponseCompleted = useCallback(() => {
    // Could refresh customer context here if needed
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Simulated ZING Website */}
      <div className="relative">
        {/* Navigation */}
        <nav className="bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#6366F1] flex items-center justify-center shadow-md">
                  <span className="text-white font-bold text-lg">Z</span>
                </div>
                <span className="text-xl font-bold text-zinc-900 dark:text-white">ZING</span>
              </div>
              <div className="hidden md:flex items-center gap-8">
                <a href="#" className="text-zinc-600 dark:text-zinc-400 hover:text-[#6366F1] transition-colors">Services</a>
                <a href="#" className="text-zinc-600 dark:text-zinc-400 hover:text-[#6366F1] transition-colors">Pricing</a>
                <a href="#" className="text-zinc-600 dark:text-zinc-400 hover:text-[#6366F1] transition-colors">About</a>
                <a href="#" className="text-zinc-600 dark:text-zinc-400 hover:text-[#6366F1] transition-colors">Contact</a>
              </div>
              <div className="flex items-center gap-4">
                <ThemeToggle value={scheme} onChange={onThemeChange} />
                <button className="bg-[#6366F1] text-white px-4 py-2 rounded-lg hover:bg-[#5558E3] transition-colors">
                  Get Started
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="bg-gradient-to-br from-[#6366F1] via-[#818CF8] to-[#A5B4FC] text-white py-20 md:py-32">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Grow Your Business Online
            </h1>
            <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto">
              Custom websites, local listings, and AI-powered tools to help your small business thrive.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-[#6366F1] px-8 py-4 rounded-lg font-semibold text-lg hover:bg-zinc-100 transition-colors shadow-lg">
                Start Free Trial
              </button>
              <button className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white/10 transition-colors">
                View Pricing
              </button>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 bg-zinc-50 dark:bg-zinc-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-zinc-900 dark:text-white">
              Everything You Need to Succeed
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white dark:bg-zinc-800 p-8 rounded-2xl shadow-lg">
                <div className="w-14 h-14 bg-[#6366F1]/10 rounded-xl flex items-center justify-center mb-6">
                  <Globe className="w-7 h-7 text-[#6366F1]" />
                </div>
                <h3 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Custom Websites</h3>
                <p className="text-zinc-600 dark:text-zinc-400">
                  Beautiful, mobile-responsive websites designed specifically for your business. Starting at $59/month.
                </p>
              </div>
              <div className="bg-white dark:bg-zinc-800 p-8 rounded-2xl shadow-lg">
                <div className="w-14 h-14 bg-[#6366F1]/10 rounded-xl flex items-center justify-center mb-6">
                  <Zap className="w-7 h-7 text-[#6366F1]" />
                </div>
                <h3 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">ZING Local</h3>
                <p className="text-zinc-600 dark:text-zinc-400">
                  Get listed on 25+ directories including Google, Yelp, and Facebook. Boost your local visibility.
                </p>
              </div>
              <div className="bg-white dark:bg-zinc-800 p-8 rounded-2xl shadow-lg">
                <div className="w-14 h-14 bg-[#6366F1]/10 rounded-xl flex items-center justify-center mb-6">
                  <MessageCircle className="w-7 h-7 text-[#6366F1]" />
                </div>
                <h3 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Quick Chat AI</h3>
                <p className="text-zinc-600 dark:text-zinc-400">
                  AI-powered chat for your website. Answer customer questions 24/7 automatically.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section className="py-20 bg-white dark:bg-zinc-950">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-zinc-900 dark:text-white">
              Trusted by Small Businesses
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-zinc-50 dark:bg-zinc-900 p-8 rounded-2xl">
                <div className="flex gap-1 mb-4">
                  {[1,2,3,4,5].map(i => <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />)}
                </div>
                <p className="text-zinc-700 dark:text-zinc-300 mb-6 text-lg">
                  "ZING helped us get online quickly and affordably. Our new website has brought in 30% more customers!"
                </p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#6366F1] rounded-full flex items-center justify-center">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-zinc-900 dark:text-white">Sarah Johnson</p>
                    <p className="text-zinc-500 dark:text-zinc-400 text-sm">Castle Rock Bakery</p>
                  </div>
                </div>
              </div>
              <div className="bg-zinc-50 dark:bg-zinc-900 p-8 rounded-2xl">
                <div className="flex gap-1 mb-4">
                  {[1,2,3,4,5].map(i => <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />)}
                </div>
                <p className="text-zinc-700 dark:text-zinc-300 mb-6 text-lg">
                  "The Quick Chat AI handles our common questions perfectly. It's like having a 24/7 receptionist!"
                </p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#6366F1] rounded-full flex items-center justify-center">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-zinc-900 dark:text-white">Mike Thompson</p>
                    <p className="text-zinc-500 dark:text-zinc-400 text-sm">Thompson Plumbing Co.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-[#6366F1]">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Grow Your Business?
            </h2>
            <p className="text-xl mb-8 text-white/90">
              Join thousands of small businesses using ZING to succeed online.
            </p>
            <button className="bg-white text-[#6366F1] px-8 py-4 rounded-lg font-semibold text-lg hover:bg-zinc-100 transition-colors shadow-lg">
              Get Started Today
            </button>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-zinc-900 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center gap-3 mb-4 md:mb-0">
                <div className="w-8 h-8 rounded-lg bg-[#6366F1] flex items-center justify-center">
                  <span className="text-white font-bold">Z</span>
                </div>
                <span className="font-bold">ZING</span>
              </div>
              <p className="text-zinc-400">© 2025 ZING. All rights reserved. Castle Rock, Colorado</p>
            </div>
          </div>
        </footer>
      </div>

      {/* Floating Chat Widget */}
      <div className="fixed bottom-6 right-6 z-50">
        {/* Chat Window */}
        {isOpen && (
          <div className="absolute bottom-20 right-0 w-[450px] h-[600px] animate-in fade-in slide-in-from-bottom-4 duration-300">
            <Card className="w-full h-full shadow-2xl border-zinc-200 dark:border-zinc-800 overflow-hidden flex flex-col">
              {/* Widget Header */}
              <div className="bg-[#6366F1] text-white px-4 py-3 flex items-center justify-between flex-shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                    <span className="font-bold text-sm">Z</span>
                  </div>
                  <div>
                    <p className="font-semibold">ZING Support</p>
                    <p className="text-xs text-white/80">AI Assistant • Online</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleClose}
                    className="p-1 hover:bg-white/10 rounded transition-colors"
                    title="Minimize"
                  >
                    <ChevronDown className="w-5 h-5" />
                  </button>
                  <button
                    onClick={handleClose}
                    className="p-1 hover:bg-white/10 rounded transition-colors"
                    title="Close"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              {/* Chat Content */}
              <div className="flex-1 overflow-hidden">
                <ChatKitPanel
                  theme={scheme}
                  onThreadChange={handleThreadChange}
                  onResponseCompleted={handleResponseCompleted}
                />
              </div>
            </Card>
          </div>
        )}

        {/* Floating Button */}
        <button
          onClick={handleToggle}
          className={`
            w-16 h-16 rounded-full shadow-lg flex items-center justify-center
            transition-all duration-300 hover:scale-110
            ${isOpen
              ? "bg-zinc-700 hover:bg-zinc-600"
              : "bg-[#6366F1] hover:bg-[#5558E3] zing-glow"
            }
          `}
          title={isOpen ? "Close chat" : "Chat with us"}
        >
          {isOpen ? (
            <X className="w-7 h-7 text-white" />
          ) : (
            <MessageCircle className="w-7 h-7 text-white" />
          )}
        </button>

        {/* Notification Badge */}
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold animate-pulse">
            1
          </span>
        )}
      </div>
    </div>
  );
}
