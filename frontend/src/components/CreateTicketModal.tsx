import { useState, useCallback, useEffect } from "react";
import { X, Ticket, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { SUPPORT_TICKET_URL } from "@/lib/config";

type Priority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

interface CreateTicketModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface FormData {
  customer_name: string;
  customer_email: string;
  subject: string;
  description: string;
  priority: Priority;
}

type SubmitStatus = "idle" | "loading" | "success" | "error";

const PRIORITY_OPTIONS: { value: Priority; label: string; color: string }[] = [
  { value: "LOW", label: "Low", color: "text-green-600" },
  { value: "MEDIUM", label: "Medium", color: "text-yellow-600" },
  { value: "HIGH", label: "High", color: "text-orange-600" },
  { value: "URGENT", label: "Urgent", color: "text-red-600" },
];

export function CreateTicketModal({
  isOpen,
  onClose,
  onSuccess,
}: CreateTicketModalProps) {
  const [formData, setFormData] = useState<FormData>({
    customer_name: "",
    customer_email: "",
    subject: "",
    description: "",
    priority: "MEDIUM",
  });
  const [status, setStatus] = useState<SubmitStatus>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setFormData({
        customer_name: "",
        customer_email: "",
        subject: "",
        description: "",
        priority: "MEDIUM",
      });
      setStatus("idle");
      setErrorMessage("");
      setSuccessMessage("");
    }
  }, [isOpen]);

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen && status !== "loading") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose, status]);

  const handleInputChange = useCallback(
    (field: keyof FormData, value: string) => {
      setFormData((prev) => ({ ...prev, [field]: value }));
    },
    []
  );

  const validateForm = useCallback((): string | null => {
    if (!formData.customer_email.trim()) {
      return "Email is required";
    }
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.customer_email.trim())) {
      return "Please enter a valid email address";
    }
    if (!formData.subject.trim()) {
      return "Subject is required";
    }
    if (!formData.description.trim()) {
      return "Description is required";
    }
    return null;
  }, [formData]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      const validationError = validateForm();
      if (validationError) {
        setErrorMessage(validationError);
        setStatus("error");
        return;
      }

      setStatus("loading");
      setErrorMessage("");

      try {
        const response = await fetch(SUPPORT_TICKET_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            customer_name: formData.customer_name.trim() || undefined,
            customer_email: formData.customer_email.trim(),
            subject: formData.subject.trim(),
            description: formData.description.trim(),
            priority: formData.priority,
          }),
        });

        const result = await response.json();

        if (result.success) {
          setStatus("success");
          setSuccessMessage(result.message);
          onSuccess?.();
          // Auto-close after success
          setTimeout(() => {
            onClose();
          }, 2000);
        } else {
          setStatus("error");
          setErrorMessage(result.message || "Failed to create ticket");
        }
      } catch (error) {
        console.error("Ticket creation error:", error);
        setStatus("error");
        setErrorMessage("Network error. Please try again.");
      }
    },
    [formData, validateForm, onClose, onSuccess]
  );

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in"
      onClick={(e) => {
        if (e.target === e.currentTarget && status !== "loading") {
          onClose();
        }
      }}
    >
      <Card className="w-full max-w-lg bg-background shadow-2xl border-border/50 animate-slide-in-bottom overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border/50 bg-gradient-to-r from-primary/5 to-transparent">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Ticket className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Create Support Ticket</h2>
              <p className="text-sm text-muted-foreground">
                We'll respond as soon as possible
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            disabled={status === "loading"}
            className="rounded-full"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Success State */}
        {status === "success" ? (
          <div className="px-6 py-12 text-center">
            <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Ticket Submitted!</h3>
            <p className="text-muted-foreground">{successMessage}</p>
          </div>
        ) : (
          /* Form */
          <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
            {/* Error Message */}
            {status === "error" && errorMessage && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {errorMessage}
              </div>
            )}

            {/* Name Field */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Name <span className="text-muted-foreground">(optional)</span>
              </label>
              <input
                type="text"
                value={formData.customer_name}
                onChange={(e) =>
                  handleInputChange("customer_name", e.target.value)
                }
                placeholder="Your name"
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                disabled={status === "loading"}
              />
            </div>

            {/* Email Field */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Email <span className="text-destructive">*</span>
              </label>
              <input
                type="email"
                value={formData.customer_email}
                onChange={(e) =>
                  handleInputChange("customer_email", e.target.value)
                }
                placeholder="your.email@company.com"
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                disabled={status === "loading"}
                required
              />
            </div>

            {/* Subject Field */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Subject <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => handleInputChange("subject", e.target.value)}
                placeholder="Brief summary of your issue"
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                disabled={status === "loading"}
                required
              />
            </div>

            {/* Description Field */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Description <span className="text-destructive">*</span>
              </label>
              <textarea
                value={formData.description}
                onChange={(e) =>
                  handleInputChange("description", e.target.value)
                }
                placeholder="Please describe your issue in detail..."
                rows={4}
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all resize-none"
                disabled={status === "loading"}
                required
              />
            </div>

            {/* Priority Field */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Priority</label>
              <select
                value={formData.priority}
                onChange={(e) =>
                  handleInputChange("priority", e.target.value as Priority)
                }
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                disabled={status === "loading"}
              >
                {PRIORITY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={status === "loading"}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={status === "loading"}
                className="flex-1 bg-primary hover:bg-primary/90"
              >
                {status === "loading" ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Ticket className="w-4 h-4 mr-2" />
                    Submit Ticket
                  </>
                )}
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}
