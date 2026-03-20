"""
Zing Customer Support Knowledge Base

Comprehensive FAQ database for answering common customer questions.
The LLM's natural language understanding handles semantic matching.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class KnowledgeBaseEntry:
    """Single knowledge base entry with question, answer, and metadata."""

    category: str
    question: str
    answer: str
    keywords: List[str]
    related_links: List[str]


# ============================================================================
# ZING KNOWLEDGE BASE
# ============================================================================

KNOWLEDGE_BASE: List[KnowledgeBaseEntry] = [
    # ============================================================================
    # VERIFIED FROM ZING.WORK BUSINESS PLAN PAGES (December 2025)
    # Source: https://www.zing.work/discover-plan, /boost-plan, /dominate-plan
    # ============================================================================

    # ========================================
    # DISCOVER PLAN - $59/month
    # Source: https://www.zing.work/discover-plan
    # ========================================
    KnowledgeBaseEntry(
        category="Plans & Pricing",
        question="What is included in the DISCOVER plan?",
        answer="The **DISCOVER plan ($59/month)** provides a complete website + essential local visibility.\n\n"
               "**What's Included:**\n"
               "• Custom 5-page website (mobile-optimized, fast, built for you - no DIY)\n"
               "• ZING Local - 10 local directory listings to boost visibility and improve local SEO\n"
               "• Up to 50 local landing pages targeting your key suburbs, cities, and service areas - 50 times more chances to be found on Google\n"
               "• AI Chat - Turn website visitors into qualified leads 24/7\n"
               "• Google Business Profile setup and optimization\n\n"
               "**One-time development fee:** $259 (billed only after your first draft is approved)\n\n"
               "**No Bots. No DIY. Real Designers.**",
        keywords=["discover", "discover plan", "59", "basic plan", "starter", "entry level", "five page", "launch fee", "development fee", "259"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    # ========================================
    # BOOST PLAN - $149/month
    # Source: https://www.zing.work/boost-plan
    # ========================================
    KnowledgeBaseEntry(
        category="Plans & Pricing",
        question="What is included in the BOOST plan?",
        answer="The **BOOST plan ($149/month)** is a marketing-ready website built to grow your business.\n\n"
               "**Everything in Discover, PLUS:**\n\n"
               "• Up to 10-page custom website\n"
               "• Up to 100 local landing pages\n"
               "• Online booking, appointments & ePayments\n"
               "• Weekly social media post & blog post (created and published for you)\n"
               "• Google Business Profile posts & ongoing optimization\n"
               "• SEO tags & Google Search Console setup\n"
               "• Built-in email marketing (10,000 emails/month)\n"
               "• Built-in SMS marketing (1,000 texts/month)\n\n"
               "**One-time development fee:** $359 (billed only after your first draft is approved)\n\n"
               "**No Bots. No DIY. Real Designers.**",
        keywords=["boost", "boost plan", "149", "middle plan", "marketing", "content", "ten page"],
        related_links=["https://www.zing.work/boost-plan"]
    ),

    # ========================================
    # DOMINATE PLAN - $249/month
    # Source: https://www.zing.work/dominate-plan
    # ========================================
    KnowledgeBaseEntry(
        category="Plans & Pricing",
        question="What is included in the DOMINATE plan?",
        answer="The **DOMINATE plan ($249/month)** is a high-performance website + advanced marketing engine.\n\n"
               "**Everything in Boost, PLUS:**\n\n"
               "• 15-page custom website\n"
               "• Up to 100 local landing pages\n"
               "• Advanced eCommerce features for larger product catalogs and enhanced checkout\n"
               "• Marketing at scale with automated campaigns: 20,000 emails/month and 2,000 texts/month\n"
               "• Concierge technical support - priority, dedicated assistance\n"
               "• Memberships functionality\n\n"
               "**One-time development fee:** $399 (billed only after your first draft is approved)\n\n"
               "**No Bots. No DIY. Real Designers.**",
        keywords=["dominate", "dominate plan", "dominator", "249", "premium", "top tier", "best plan", "maximum", "advanced", "concierge", "development fee", "399"],
        related_links=["https://www.zing.work/dominate-plan"]
    ),

    # ========================================
    # PLAN COMPARISON & PRICING
    # ========================================
    KnowledgeBaseEntry(
        category="Plans & Pricing",
        question="What plans does ZING offer and how much do they cost?",
        answer="ZING offers three business plans:\n\n"
               "**DISCOVER - $59/month**\n"
               "A complete website + essential local visibility\n"
               "• 5-page custom website\n"
               "• 10 local directory listings\n"
               "• Up to 50 local landing pages\n"
               "• AI Chat for 24/7 lead capture\n"
               "• Google Business Profile setup and optimization\n\n"
               "**BOOST - $149/month**\n"
               "A marketing-ready website built to grow your business\n"
               "• Up to 10-page custom website\n"
               "• Up to 100 local landing pages\n"
               "• Weekly social media & blog content\n"
               "• SEO tags & Google Search Console\n"
               "• 10,000 emails + 1,000 texts/month\n"
               "• Online booking & ePayments\n\n"
               "**DOMINATE - $249/month**\n"
               "High-performance website + advanced marketing engine\n"
               "• 15-page custom website\n"
               "• Up to 100 local landing pages\n"
               "• Advanced eCommerce\n"
               "• 20,000 emails + 2,000 texts/month with automated campaigns\n"
               "• Concierge technical support\n\n"
               "**No contracts required.** One-time development fee per plan: DISCOVER $259, BOOST $359, DOMINATE $399 (billed only after first draft is approved).",
        keywords=["plans", "pricing", "compare", "cost", "price", "how much", "which plan", "difference", "features", "monthly"],
        related_links=["https://www.zing.work/discover-plan", "https://www.zing.work/boost-plan", "https://www.zing.work/dominate-plan"]
    ),

    # ========================================
    # COMMON FAQs (Verified from all plan pages)
    # ========================================
    KnowledgeBaseEntry(
        category="Account & Billing",
        question="Why is ZING so affordable?",
        answer="ZING is affordable because we focus on building lasting relationships with our customers and rely on word-of-mouth marketing rather than expensive marketing campaigns.\n\n"
               "This allows us to pass the savings directly to our customers while still providing agency-level website design and marketing services.",
        keywords=["affordable", "cheap", "low cost", "why so cheap", "how affordable", "value", "price"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    KnowledgeBaseEntry(
        category="Account & Billing",
        question="Do I own my website content?",
        answer="**Yes!** You own all the website content.\n\n"
               "If you ever decide to leave ZING, you can easily export your site content without any hassle.",
        keywords=["own", "ownership", "content", "my website", "leave", "export", "transfer", "keep"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    KnowledgeBaseEntry(
        category="Account & Billing",
        question="Does ZING require contracts?",
        answer="**No, we don't require contracts.**\n\n"
               "Our commitment to quality service ensures that our customers stay with us by choice, not obligation.\n\n"
               "• Month-to-month billing\n"
               "• No setup fees\n"
               "• No cancellation penalties\n"
               "• Incredible value, no lock-in",
        keywords=["contract", "contracts", "cancel", "cancellation", "commitment", "locked in", "long term", "monthly"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    KnowledgeBaseEntry(
        category="General",
        question="What kind of websites does ZING design?",
        answer="We design a wide variety of websites, from simple anchored websites to full comprehensive business sites, ensuring they are both visually appealing and highly functional to meet your specific needs.\n\n"
               "Every ZING website is:\n"
               "• Custom designed (no templates)\n"
               "• Mobile-optimized\n"
               "• Fast-loading\n"
               "• Built by real US-based designers",
        keywords=["websites", "design", "types", "what kind", "custom", "template"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    KnowledgeBaseEntry(
        category="General",
        question="Where is ZING located?",
        answer="ZING is based in **Castle Rock, Colorado, USA** and proudly serves clients both locally and globally.\n\n"
               "**Contact:**\n"
               "• Phone: 1-888-716-1113\n"
               "• Address: 333 Perry Street, Castle Rock, CO 80104\n\n"
               "🇺🇸 Our designers are US-based.",
        keywords=["location", "where", "based", "office", "castle rock", "colorado", "address", "usa", "united states"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    KnowledgeBaseEntry(
        category="General",
        question="What industries does ZING work with?",
        answer="We work with all types of businesses, including:\n\n"
               "• Contractors & home services\n"
               "• Professional services\n"
               "• Health services\n"
               "• Restaurants\n"
               "• Advisory services\n"
               "• Wellness providers\n\n"
               "We can customize our platform for virtually any industry.",
        keywords=["industry", "industries", "business type", "contractors", "restaurants", "healthcare", "professional services", "who do you work with"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    # ========================================
    # FEATURES (Verified from plan pages)
    # ========================================
    KnowledgeBaseEntry(
        category="Features",
        question="What is ZING Local?",
        answer="**ZING Local** gets your business listed on local directories to boost visibility and improve your local SEO rankings.\n\n"
               "We create local landing pages targeting your key suburbs, cities, and service areas, helping you appear in more local searches and on Google Maps.\n\n"
               "**Landing Pages by Plan:**\n"
               "• DISCOVER: Up to 50 local landing pages\n"
               "• BOOST: Up to 100 local landing pages\n"
               "• DOMINATE: Up to 100 local landing pages",
        keywords=["zing local", "local seo", "directory", "listings", "local visibility", "near me", "landing pages", "local landing"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    KnowledgeBaseEntry(
        category="Features",
        question="What is ZING AI Chat?",
        answer="**AI Chat** turns website visitors into qualified leads with the power of an AI chatbot that engages, answers questions, and captures contact details - all in real time, 24/7.\n\n"
               "**Included in:** All plans (DISCOVER, BOOST, and DOMINATE)",
        keywords=["ai chat", "chatbot", "chat widget", "live chat", "24/7", "lead capture", "quick chat"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    KnowledgeBaseEntry(
        category="Features",
        question="What Google Business Profile services does ZING offer?",
        answer="All ZING plans include **Google Business Profile Optimization** to beat your local competition with increased visibility in local searches, more traffic, and high-intent customers.\n\n"
               "**BOOST & DOMINATE Plans** also include:\n"
               "• Weekly Google Business Profile posts\n"
               "• Ongoing optimization",
        keywords=["google business", "google my business", "gbp", "google profile", "google maps", "local search"],
        related_links=["https://www.zing.work/boost-plan"]
    ),

    KnowledgeBaseEntry(
        category="Features",
        question="Does ZING offer online booking?",
        answer="**Yes!** Online booking and appointments are available.\n\n"
               "**BOOST & DOMINATE plans include:**\n"
               "• Online booking portal\n"
               "• Appointment scheduling\n"
               "• ePayments integration\n\n"
               "Let customers book services anytime with built-in scheduling and simple checkout.",
        keywords=["booking", "appointments", "schedule", "calendar", "online booking", "book online", "scheduling", "epayments"],
        related_links=["https://www.zing.work/boost-plan"]
    ),

    KnowledgeBaseEntry(
        category="Features",
        question="How does email and SMS marketing work with ZING?",
        answer="ZING includes built-in email and SMS marketing (BOOST and DOMINATE plans).\n\n"
               "**BOOST Plan:**\n"
               "• 10,000 emails per month\n"
               "• 1,000 text messages per month\n\n"
               "**DOMINATE Plan:**\n"
               "• 20,000 emails per month\n"
               "• 2,000 text messages per month\n\n"
               "Reach customers with promos, reminders, and review requests.",
        keywords=["email", "sms", "text", "marketing", "emails per month", "texts per month", "newsletter", "campaigns"],
        related_links=["https://www.zing.work/boost-plan", "https://www.zing.work/dominate-plan"]
    ),

    KnowledgeBaseEntry(
        category="Features",
        question="Does ZING offer eCommerce?",
        answer="**Yes!** ZING offers eCommerce functionality.\n\n"
               "**BOOST Plan:** Online booking & ePayments included\n\n"
               "**DOMINATE Plan:** Advanced eCommerce features - larger product catalogs, enhanced checkout experiences, and tools to drive higher sales and engagement.",
        keywords=["ecommerce", "online store", "sell online", "payments", "shop", "products"],
        related_links=["https://www.zing.work/dominate-plan"]
    ),

    KnowledgeBaseEntry(
        category="Features",
        question="What is Concierge Technical Support?",
        answer="**Concierge Technical Support** is priority, dedicated technical assistance available with the **DOMINATE plan**.\n\n"
               "Our team is ready to assist with any technical needs, updates, or troubleshooting to keep your site running smoothly - with faster response times than standard support.",
        keywords=["concierge", "priority support", "technical support", "premium support", "dominate support"],
        related_links=["https://www.zing.work/dominate-plan"]
    ),

    # ========================================
    # CONTACT & SUPPORT
    # ========================================
    KnowledgeBaseEntry(
        category="Support",
        question="How do I contact ZING?",
        answer="**Phone:** 1-888-716-1113\n\n"
               "Talk to our business experts and we will have your website live fast. And yes we are real people and pick up the phone!\n\n"
               "**Email:** support@zing-work.com\n\n"
               "**Business Hours:** Monday to Friday, 9am to 5pm MST\n\n"
               "**This Chat:** I can answer many questions right now, or connect you with our team for complex issues.\n\n"
               "🇺🇸 Our designers are US-based.",
        keywords=["contact", "support", "help", "phone", "reach", "call", "talk to someone", "email", "hours"],
        related_links=["https://www.zing.work/discover-plan"]
    ),

    # ========================================
    # BUSINESS HOURS & RESPONSE TIMES
    # ========================================
    KnowledgeBaseEntry(
        category="Support",
        question="What are ZING's business hours?",
        answer="**Business Hours:** Monday to Friday, 9am to 5pm MST\n\n"
               "**Phone:** 1-888-716-1113\n"
               "**Email:** support@zing-work.com\n\n"
               "Our team responds to support requests within 24 business hours.",
        keywords=["hours", "business hours", "open", "available", "when", "time", "response time", "how long"],
        related_links=[]
    ),

    # ========================================
    # CANCELLATION & SELF-SERVICE
    # ========================================
    KnowledgeBaseEntry(
        category="Account & Billing",
        question="How do I cancel my ZING subscription?",
        answer="ZING has **no contracts** - you can cancel at any time directly from your account.\n\n"
               "**To cancel:**\n"
               "1. Log in to your ZING account\n"
               "2. Go to **Billing**\n"
               "3. Select **Cancel, Update, or Change Subscription**\n\n"
               "If you are having trouble accessing your account, reach out to our support team at support@zing-work.com and we will help you.",
        keywords=["cancel", "cancellation", "cancel subscription", "stop", "end", "quit", "unsubscribe", "close account"],
        related_links=[]
    ),

    KnowledgeBaseEntry(
        category="Account & Billing",
        question="How do I view my receipts or payment history?",
        answer="All your receipts and payment history are available in your ZING account.\n\n"
               "**To view:**\n"
               "1. Log in to your ZING account\n"
               "2. Go to **Billing**\n"
               "3. View and download your full history and receipts from there\n\n"
               "If you cannot log in, contact our support team at support@zing-work.com for help.",
        keywords=["receipt", "receipts", "invoice", "payment history", "billing history", "charges", "statement"],
        related_links=[]
    ),

    KnowledgeBaseEntry(
        category="Account & Billing",
        question="I have a billing issue (failed payment, charge question, or dispute)",
        answer="For billing issues including failed payments, charge questions, overdue invoices, disputes, or account pauses, please contact our support team.\n\n"
               "**Email:** support@zing-work.com\n"
               "**Phone:** 1-888-716-1113\n\n"
               "Our team will review your issue and get back to you within **24 business hours** (Monday to Friday, 9am to 5pm MST).",
        keywords=["billing", "payment", "failed payment", "charge", "dispute", "overdue", "invoice", "pause", "refund"],
        related_links=[]
    ),

    # ========================================
    # UPGRADE / DOWNGRADE
    # ========================================
    KnowledgeBaseEntry(
        category="Account & Billing",
        question="How do I upgrade or downgrade my ZING plan?",
        answer="If you would like to upgrade, downgrade, or learn about other ZING products, our team can help.\n\n"
               "**Contact support:** support@zing-work.com or call 1-888-716-1113\n\n"
               "A team member will review your current plan and help you find the best fit. Response within **24 business hours** (Monday to Friday, 9am to 5pm MST).",
        keywords=["upgrade", "downgrade", "change plan", "switch plan", "different plan", "more features", "not enough"],
        related_links=[]
    ),

    # ========================================
    # DESIGN PROCESS
    # ========================================
    KnowledgeBaseEntry(
        category="Design",
        question="How long does it take to get my website?",
        answer="Your custom website is built and your **first draft is ready within 5 to 7 business days** after signup.\n\n"
               "Your first draft will be sent to the email address you signed up with. Be sure to check your **junk/spam folder** as design emails can sometimes get filtered.\n\n"
               "The one-time development fee (DISCOVER $259, BOOST $359, DOMINATE $399) is only billed after you have reviewed and approved your draft.",
        keywords=["how long", "turnaround", "timeline", "when", "first draft", "website ready", "delivery", "build time", "5 days", "7 days"],
        related_links=[]
    ),

    KnowledgeBaseEntry(
        category="Design",
        question="I haven't received my first draft or need to discuss edits",
        answer="**If you haven't received your first draft:**\n"
               "1. Check the inbox of the email address you signed up with\n"
               "2. Check your **junk/spam folder** - design emails sometimes get filtered there\n"
               "3. If you still can't find it, contact support at support@zing-work.com and we will get it sorted\n\n"
               "**If you have your draft and want to discuss edits:**\n"
               "The email with your first draft includes a link to **book a call directly with your designer** at a time that suits you.\n\n"
               "**For changes to a live site:**\n"
               "Use the edits request form at the bottom of the zing.work website.\n\n"
               "Our team responds within **24 business hours** (Monday to Friday, 9am to 5pm MST).",
        keywords=["first draft", "draft", "edits", "edit", "changes", "designer", "design", "website design", "not received", "missing draft", "live site changes"],
        related_links=["https://www.zing.work"]
    ),

    # ========================================
    # SEO EXPECTATIONS
    # ========================================
    KnowledgeBaseEntry(
        category="Features",
        question="How long does SEO take to start working?",
        answer="SEO is a gradual process. You can typically expect to **start seeing results within 3 to 6 weeks** after your site goes live.\n\n"
               "ZING helps accelerate this with:\n"
               "• Local landing pages targeting your service areas\n"
               "• Google Business Profile setup and optimization\n"
               "• SEO tags and Google Search Console setup (BOOST & DOMINATE)\n"
               "• Weekly content publishing (BOOST & DOMINATE)\n\n"
               "If you have questions about your SEO performance, contact our support team at support@zing-work.com.",
        keywords=["seo", "search engine", "google ranking", "how long seo", "not showing up", "not ranking", "traffic", "visibility", "search results"],
        related_links=[]
    ),

    # ========================================
    # SUPPORT SCOPE
    # ========================================
    KnowledgeBaseEntry(
        category="Support",
        question="What can ZING support help me with?",
        answer="Our support team can help with a wide range of issues including:\n\n"
               "• **Account access** - Login issues, password resets\n"
               "• **Technical issues** - Website not loading, publishing problems, platform issues\n"
               "• **SEO & statistics** - Questions about your site performance\n"
               "• **Onboarding setup** - Landing pages, AI Chat, social media, Google Business Profile, blogs, local listings\n"
               "• **Billing** - Payment issues, charge questions, plan changes\n"
               "• **Design** - First draft questions, edit requests, live site changes\n\n"
               "**Contact:** support@zing-work.com or call 1-888-716-1113\n"
               "**Hours:** Monday to Friday, 9am to 5pm MST\n"
               "**Response time:** Within 24 business hours",
        keywords=["support", "help", "what can you help with", "issues", "problems", "assistance", "technical"],
        related_links=[]
    ),
]


# ============================================================================
# KNOWLEDGE BASE SEARCH ENGINE
# ============================================================================

class KnowledgeBaseSearch:
    """
    Knowledge base search that leverages the LLM's natural language understanding.

    Returns ALL relevant entries and lets the LLM determine the best match
    based on semantic understanding - NOT simple keyword/regex matching.
    """

    def __init__(self, knowledge_base: List[KnowledgeBaseEntry]):
        self.kb = knowledge_base

    def search(self, query: str, max_results: int = 10) -> List[KnowledgeBaseEntry]:
        """
        Return KB entries for the LLM to semantically match.

        The LLM has natural language inference built-in and can understand
        that "What's the price for a site?" matches "How much do Zing services cost?"

        We return a generous set of entries and trust the LLM to find the best match.
        """
        query_lower = query.lower()
        query_words = [w for w in query_lower.split() if len(w) > 2]

        # Score entries with loose matching - we WANT to include more results
        # so the LLM can use its semantic understanding to pick the best one
        scored_entries = []
        for entry in self.kb:
            score = 0

            # Check keywords (loose matching)
            for keyword in entry.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in query_lower:
                    score += 3
                # Also check if any query word appears in keyword
                for word in query_words:
                    if word in keyword_lower or keyword_lower in word:
                        score += 1

            # Check question text (loose matching)
            question_lower = entry.question.lower()
            for word in query_words:
                if word in question_lower:
                    score += 2

            # Check answer text (loose matching for context)
            answer_lower = entry.answer.lower()
            for word in query_words:
                if word in answer_lower:
                    score += 1

            # Check category
            category_lower = entry.category.lower()
            for word in query_words:
                if word in category_lower:
                    score += 1

            if score > 0:
                scored_entries.append((score, entry))

        # Sort by score descending
        scored_entries.sort(key=lambda x: x[0], reverse=True)

        # Return more results than before - let the LLM decide
        return [entry for score, entry in scored_entries[:max_results]]

    def get_all_entries(self) -> List[KnowledgeBaseEntry]:
        """Return ALL knowledge base entries for comprehensive search."""
        return self.kb.copy()

    def get_by_category(self, category: str) -> List[KnowledgeBaseEntry]:
        """Get all entries in a specific category."""
        return [entry for entry in self.kb if entry.category == category]

    def get_all_categories(self) -> List[str]:
        """Get list of all unique categories."""
        return sorted(list(set(entry.category for entry in self.kb)))


# Initialize global search engine
kb_search = KnowledgeBaseSearch(KNOWLEDGE_BASE)
