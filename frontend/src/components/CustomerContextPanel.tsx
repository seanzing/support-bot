import { Clock } from "lucide-react";
import type { CustomerProfile } from "../hooks/useCustomerContext";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

type CustomerContextPanelProps = {
  profile: CustomerProfile | null;
  loading: boolean;
  error: string | null;
};

export function CustomerContextPanel({ profile, loading, error }: CustomerContextPanelProps) {
  if (loading) {
    return <SkeletonState />;
  }

  if (error) {
    return (
      <Card className="border-red-200/80 dark:border-red-900/50 animate-scale-in shadow-card">
        <CardContent className="p-6">
          <div className="text-sm text-red-600 dark:text-red-400 font-medium">{error}</div>
        </CardContent>
      </Card>
    );
  }

  if (!profile) {
    return (
      <Card className="flex min-h-[300px] sm:min-h-[350px] md:min-h-[400px] flex-col items-center justify-center animate-scale-in shadow-card border-border/50">
        <CardContent className="p-4 sm:p-5 md:p-6 flex flex-col items-center justify-center">
          <div className="relative mb-2 sm:mb-3">
            <Clock className="h-8 w-8 sm:h-9 sm:w-9 md:h-10 md:w-10 text-muted-foreground/60" />
            <div className="absolute inset-0 bg-muted/20 rounded-full blur-xl animate-pulse-subtle" />
          </div>
          <p className="text-xs sm:text-sm text-muted-foreground font-medium text-center">
            Start a conversation to see details
          </p>
        </CardContent>
      </Card>
    );
  }

  const questionsAsked = profile.questions_asked || 0;
  const articlesViewed = profile.kb_articles_viewed || 0;
  const ticketsCreated = profile.tickets_created || 0;
  const interactions = profile.interactions || [];

  return (
    <Card className="shadow-card hover:shadow-elevated transition-all duration-300 animate-scale-in border-border/50 relative overflow-hidden group">
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.02] via-transparent to-accent/[0.01] opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      <CardContent className="p-4 sm:p-5 md:p-6 space-y-4 sm:space-y-5 md:space-y-6 relative">
        {/* Header - Enhanced with gradient and animation - Responsive */}
        <div className="space-y-1">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm sm:text-base font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text truncate">
              {profile.customer_name || "Guest"}
            </h2>
            <Badge variant="secondary" className="gap-1 sm:gap-1.5 shadow-subtle border border-border/40 shrink-0">
              <div className="h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full bg-emerald-500 animate-pulse-subtle shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
              <span className="text-[10px] sm:text-xs font-medium">Active</span>
            </Badge>
          </div>
          {profile.customer_email && (
            <p className="mt-1 sm:mt-1.5 text-xs sm:text-sm text-muted-foreground font-medium truncate">
              {profile.customer_email}
            </p>
          )}
        </div>

        <Separator className="bg-border/40" />

        {/* Stats - Responsive grid: 1 col mobile, 2 col tablet, 3 col desktop */}
        <div>
          <h3 className="mb-3 sm:mb-4 text-[10px] sm:text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Session Stats
          </h3>
          <TooltipProvider>
            <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-2.5 md:gap-3">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="group cursor-default p-2.5 sm:p-3 rounded-lg border border-border/40 bg-card/50 hover:bg-accent/20 hover:border-primary/30 transition-all duration-200 hover:shadow-card">
                    <div className="text-xl sm:text-2xl font-bold group-hover:text-primary transition-colors duration-200">
                      {questionsAsked}
                    </div>
                    <div className="mt-0.5 sm:mt-1 text-[10px] sm:text-xs text-muted-foreground font-medium">
                      Questions
                    </div>
                  </div>
                </TooltipTrigger>
                <TooltipContent className="font-medium text-xs">
                  <p>Questions asked in this session</p>
                </TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="group cursor-default p-2.5 sm:p-3 rounded-lg border border-border/40 bg-card/50 hover:bg-accent/20 hover:border-primary/30 transition-all duration-200 hover:shadow-card">
                    <div className="text-xl sm:text-2xl font-bold group-hover:text-primary transition-colors duration-200">
                      {articlesViewed}
                    </div>
                    <div className="mt-0.5 sm:mt-1 text-[10px] sm:text-xs text-muted-foreground font-medium">
                      Articles
                    </div>
                  </div>
                </TooltipTrigger>
                <TooltipContent className="font-medium text-xs">
                  <p>Knowledge base articles viewed</p>
                </TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="group cursor-default p-2.5 sm:p-3 rounded-lg border border-border/40 bg-card/50 hover:bg-accent/20 hover:border-primary/30 transition-all duration-200 hover:shadow-card xs:col-span-2 sm:col-span-1">
                    <div className="text-xl sm:text-2xl font-bold group-hover:text-primary transition-colors duration-200">
                      {ticketsCreated}
                    </div>
                    <div className="mt-0.5 sm:mt-1 text-[10px] sm:text-xs text-muted-foreground font-medium">
                      Tickets
                    </div>
                  </div>
                </TooltipTrigger>
                <TooltipContent className="font-medium text-xs">
                  <p>Support tickets created</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </TooltipProvider>
        </div>

        <Separator className="bg-border/40" />

        {/* Activity - Enhanced timeline with responsive adjustments */}
        <div>
          <h3 className="mb-3 sm:mb-4 text-[10px] sm:text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Recent Activity
          </h3>
          {interactions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-6 sm:py-8 text-center">
              <div className="h-10 w-10 sm:h-12 sm:w-12 rounded-full bg-muted/40 flex items-center justify-center mb-2 sm:mb-3">
                <Clock className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground" />
              </div>
              <p className="text-xs sm:text-sm text-muted-foreground font-medium">No activity yet</p>
            </div>
          ) : (
            <div className="space-y-3 sm:space-y-4">
              {interactions.map((interaction, index: number) => (
                <div
                  key={interaction.timestamp + "-" + index}
                  className="group relative pl-3 sm:pl-4 border-l-2 border-border/60 hover:border-primary/60 transition-all duration-200"
                >
                  <div className="absolute left-[-5px] top-[6px] h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full bg-muted-foreground/60 group-hover:bg-primary group-hover:shadow-[0_0_6px_currentColor] transition-all duration-200" />
                  <div className="group-hover:translate-x-0.5 transition-transform duration-200">
                    <p className="text-xs sm:text-sm leading-relaxed font-medium group-hover:text-foreground transition-colors duration-200">
                      {interaction.description}
                    </p>
                    <p className="mt-1 sm:mt-1.5 text-[10px] sm:text-xs text-muted-foreground font-medium">
                      {formatTimestamp(interaction.timestamp)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function SkeletonState() {
  return (
    <Card className="animate-scale-in shadow-card border-border/50 overflow-hidden">
      <CardContent className="p-4 sm:p-5 md:p-6 space-y-4 sm:space-y-5 md:space-y-6">
        {/* Header skeleton with shimmer - Responsive */}
        <div className="space-y-2 sm:space-y-3">
          <div className="flex items-center justify-between gap-2">
            <Skeleton className="h-5 sm:h-6 w-24 sm:w-32 animate-shimmer" />
            <Skeleton className="h-4 sm:h-5 w-14 sm:w-16 rounded-full animate-shimmer" />
          </div>
          <Skeleton className="h-3 sm:h-4 w-36 sm:w-48 animate-shimmer" />
        </div>

        <Separator className="bg-border/40" />

        {/* Stats skeleton - Responsive grid layout */}
        <div className="space-y-3 sm:space-y-4">
          <Skeleton className="h-2.5 sm:h-3 w-16 sm:w-20 animate-shimmer" />
          <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-2.5 md:gap-3">
            {[1, 2, 3].map(i => (
              <div
                key={i}
                className={`p-2.5 sm:p-3 rounded-lg border border-border/40 bg-card/50 space-y-1.5 sm:space-y-2 ${i === 3 ? 'xs:col-span-2 sm:col-span-1' : ''}`}
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <Skeleton className="h-6 sm:h-8 w-10 sm:w-12 animate-shimmer" />
                <Skeleton className="h-2.5 sm:h-3 w-12 sm:w-16 animate-shimmer" />
              </div>
            ))}
          </div>
        </div>

        <Separator className="bg-border/40" />

        {/* Activity skeleton - Responsive timeline */}
        <div className="space-y-3 sm:space-y-4">
          <Skeleton className="h-2.5 sm:h-3 w-20 sm:w-24 animate-shimmer" />
          <div className="space-y-3 sm:space-y-4">
            {[1, 2].map(i => (
              <div
                key={i}
                className="relative pl-3 sm:pl-4 border-l-2 border-border/60 space-y-1.5 sm:space-y-2"
                style={{ animationDelay: `${i * 0.15}s` }}
              >
                <div className="absolute left-[-5px] top-[6px] h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full bg-muted-foreground/40 animate-pulse-subtle" />
                <Skeleton className="h-3 sm:h-4 w-full animate-shimmer" />
                <Skeleton className="h-2.5 sm:h-3 w-16 sm:w-20 animate-shimmer" />
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function formatTimestamp(value: string): string {
  try {
    const date = new Date(value);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    return date.toLocaleDateString();
  } catch {
    return value;
  }
}
