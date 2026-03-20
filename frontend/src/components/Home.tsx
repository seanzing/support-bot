import { useCallback, useState } from "react";
import { Ticket, MessageSquarePlus } from "lucide-react";

import { ChatKitPanel, THREAD_STORAGE_KEY } from "./ChatKitPanel";
import { CustomerContextPanel } from "./CustomerContextPanel";
import { CreateTicketModal } from "./CreateTicketModal";
import { ThemeToggle } from "./ThemeToggle";
import { Button } from "@/components/ui/button";
import { useCustomerContext } from "../hooks/useCustomerContext";
import type { ColorScheme } from "../hooks/useColorScheme";
import { Card } from "@/components/ui/card";

type HomeProps = {
  scheme: ColorScheme;
  onThemeChange: (scheme: ColorScheme) => void;
};

export default function Home({ scheme, onThemeChange }: HomeProps) {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [isTicketModalOpen, setIsTicketModalOpen] = useState(false);
  const [resetKey, setResetKey] = useState(0);
  const { profile, loading, error, refresh } = useCustomerContext(threadId);

  const handleThreadChange = useCallback((nextThreadId: string | null) => {
    setThreadId(nextThreadId);
  }, []);

  const handleResponseCompleted = useCallback(() => {
    void refresh();
  }, [refresh]);

  const handleOpenTicketModal = useCallback(() => {
    setIsTicketModalOpen(true);
  }, []);

  const handleCloseTicketModal = useCallback(() => {
    setIsTicketModalOpen(false);
  }, []);

  const handleTicketSuccess = useCallback(() => {
    // Refresh customer context to update ticket count
    void refresh();
  }, [refresh]);

  const handleNewChat = useCallback(() => {
    // Clear stored thread from localStorage
    try {
      localStorage.removeItem(THREAD_STORAGE_KEY);
    } catch {
      // localStorage may be unavailable
    }
    // Increment resetKey to force ChatKitPanel remount with fresh state
    setResetKey((prev) => prev + 1);
    // Clear thread ID
    setThreadId(null);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-background transition-colors duration-300">
      <div className="mx-auto max-w-[2000px]">
        {/* Header - Enhanced glass morphism with optimized spacing */}
        <header className="glass-strong border-b border-border/40 px-3 py-2.5 sm:px-4 sm:py-3 md:px-4 md:py-3 lg:px-4 lg:py-3.5 sticky top-0 z-10 shadow-subtle">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 sm:gap-3 animate-fade-in">
              {/* ZING Logo */}
              <div className="flex-shrink-0 w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-[#6366F1] flex items-center justify-center shadow-md zing-glow">
                <span className="text-white font-bold text-sm sm:text-base">Z</span>
              </div>
              <div className="space-y-0.5">
                <h1 className="text-base sm:text-lg md:text-xl font-bold tracking-tight zing-gradient-text">
                  ZING Support
                </h1>
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  AI Assistant
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 animate-fade-in" style={{ animationDelay: "0.1s" }}>
              {/* New Chat - Desktop */}
              <Button
                variant="outline"
                size="sm"
                onClick={handleNewChat}
                className="hidden sm:flex items-center gap-2 text-xs font-medium"
              >
                <MessageSquarePlus className="w-4 h-4" />
                New Chat
              </Button>
              {/* New Chat - Mobile */}
              <Button
                variant="outline"
                size="icon"
                onClick={handleNewChat}
                className="sm:hidden"
                title="New Chat"
              >
                <MessageSquarePlus className="w-4 h-4" />
              </Button>
              {/* Create Ticket - Desktop */}
              <Button
                variant="outline"
                size="sm"
                onClick={handleOpenTicketModal}
                className="hidden sm:flex items-center gap-2 text-xs font-medium"
              >
                <Ticket className="w-4 h-4" />
                Create Ticket
              </Button>
              {/* Create Ticket - Mobile */}
              <Button
                variant="outline"
                size="icon"
                onClick={handleOpenTicketModal}
                className="sm:hidden"
                title="Create Ticket"
              >
                <Ticket className="w-4 h-4" />
              </Button>
              <ThemeToggle value={scheme} onChange={onThemeChange} />
            </div>
          </div>
        </header>

        {/* Main Content - Optimized spacing for more chat real estate */}
        <main className="grid gap-3 p-3 sm:gap-3 sm:p-3 md:gap-4 md:p-4 lg:gap-4 lg:p-4 lg:grid-cols-[1fr_380px] xl:grid-cols-[1fr_420px] 2xl:grid-cols-[1fr_480px] lg:h-[calc(100vh-68px)] md:h-[calc(100vh-64px)] sm:h-[calc(100vh-60px)]">
          {/* Chat Panel - Enhanced shadow and gradient border */}
          <div className="animate-slide-in-bottom min-h-[500px] sm:min-h-[600px] lg:min-h-0" style={{ animationDelay: "0.1s" }}>
            <Card className="flex flex-col shadow-card hover:shadow-elevated transition-all duration-300 border-border/50 relative group h-full overflow-hidden p-0">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
              <ChatKitPanel
                key={resetKey}
                theme={scheme}
                onThreadChange={handleThreadChange}
                onResponseCompleted={handleResponseCompleted}
                resetKey={resetKey}
              />
            </Card>
          </div>

          {/* Context Panel - Enhanced animations and depth - Stacks on mobile/tablet */}
          <div className="animate-slide-in-bottom" style={{ animationDelay: "0.2s" }}>
            <CustomerContextPanel
              profile={profile}
              loading={loading}
              error={error}
            />
          </div>
        </main>
      </div>

      {/* Create Ticket Modal */}
      <CreateTicketModal
        isOpen={isTicketModalOpen}
        onClose={handleCloseTicketModal}
        onSuccess={handleTicketSuccess}
      />
    </div>
  );
}
