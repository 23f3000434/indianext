"""
safewaves Recommendation Engine
=================================
Generates prioritised, actionable security recommendations based on
threat type, severity level, and observed feature data.
"""

from __future__ import annotations

from typing import Any, Dict, List


class RecommendationEngine:
    """Generate context-aware security recommendations for detected threats."""

    # ------------------------------------------------------------------
    # Recommendation database
    # ------------------------------------------------------------------
    # Each threat type maps to a list of recommendation dicts. Each entry
    # includes a minimum severity tier for inclusion and the recommendation
    # details. Severity tiers are ordered: safe < low < medium < high < critical.
    # ------------------------------------------------------------------

    _SEVERITY_ORDER = {
        "safe": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    _RECOMMENDATIONS: Dict[str, List[Dict[str, Any]]] = {
        # ---------------------------------------------------------------
        # Phishing
        # ---------------------------------------------------------------
        "phishing": [
            {
                "action": "Do not click any links in the email",
                "priority": "immediate",
                "description": (
                    "Links in this email may lead to credential-harvesting pages or "
                    "malware downloads. Avoid clicking any URLs, buttons, or embedded images."
                ),
                "min_severity": "low",
            },
            {
                "action": "Report this email to your IT/security team",
                "priority": "immediate",
                "description": (
                    "Forward this email to your organisation's security team or IT "
                    "helpdesk so they can investigate and warn other users."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Mark the email as spam/phishing",
                "priority": "high",
                "description": (
                    "Use your email client's built-in reporting feature to mark this "
                    "message as phishing. This helps improve spam filters for everyone."
                ),
                "min_severity": "low",
            },
            {
                "action": "Delete the email permanently",
                "priority": "high",
                "description": (
                    "Remove the email from your inbox and deleted items to prevent "
                    "accidental interaction in the future."
                ),
                "min_severity": "high",
            },
            {
                "action": "Verify the sender through an independent channel",
                "priority": "medium",
                "description": (
                    "If the email claims to be from a known contact or organisation, "
                    "reach out to them directly via phone or their official website to "
                    "confirm whether the message is legitimate."
                ),
                "min_severity": "low",
            },
            {
                "action": "Change passwords for any accounts mentioned",
                "priority": "immediate",
                "description": (
                    "If you have already interacted with this email or its links, "
                    "immediately change the passwords for any accounts that may have "
                    "been exposed and enable two-factor authentication."
                ),
                "min_severity": "critical",
            },
        ],

        # ---------------------------------------------------------------
        # Malicious URL
        # ---------------------------------------------------------------
        "malicious_url": [
            {
                "action": "Do not visit this URL",
                "priority": "immediate",
                "description": (
                    "This URL shows characteristics of a malicious website. Avoid "
                    "visiting it in any browser to prevent exposure to phishing pages, "
                    "malware, or exploit kits."
                ),
                "min_severity": "low",
            },
            {
                "action": "Block this URL at your firewall or DNS level",
                "priority": "immediate",
                "description": (
                    "Add this URL and its domain to your organisation's blocklist in "
                    "the firewall, proxy, or DNS filter to prevent other users from "
                    "accessing it."
                ),
                "min_severity": "high",
            },
            {
                "action": "Report this URL to security services",
                "priority": "high",
                "description": (
                    "Submit this URL to services like Google Safe Browsing, PhishTank, "
                    "or VirusTotal to help protect the broader internet community."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Scan your device with antivirus software",
                "priority": "high",
                "description": (
                    "If you have already visited this URL, run a full antivirus scan "
                    "on your device immediately to detect and remove any malware that "
                    "may have been downloaded."
                ),
                "min_severity": "high",
            },
            {
                "action": "Check browser history for previous visits",
                "priority": "medium",
                "description": (
                    "Search your browser history to determine if you or other users "
                    "have previously visited this URL and assess potential exposure."
                ),
                "min_severity": "low",
            },
        ],

        # ---------------------------------------------------------------
        # Deepfake
        # ---------------------------------------------------------------
        "deepfake": [
            {
                "action": "Do not trust this media at face value",
                "priority": "immediate",
                "description": (
                    "This media shows signs of manipulation or AI generation. Do not "
                    "use it as evidence or share it as authentic content without further "
                    "verification."
                ),
                "min_severity": "low",
            },
            {
                "action": "Verify the source of this media",
                "priority": "high",
                "description": (
                    "Trace the origin of this media back to its original source. Check "
                    "metadata, publication dates, and the credibility of the source to "
                    "determine authenticity."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Report this content to the platform",
                "priority": "high",
                "description": (
                    "If this media was found on a social media platform or website, "
                    "report it as potentially manipulated content using the platform's "
                    "reporting tools."
                ),
                "min_severity": "high",
            },
            {
                "action": "Perform a reverse image search",
                "priority": "medium",
                "description": (
                    "Use reverse image search tools (e.g. Google Images, TinEye) to "
                    "find the original version of this image and identify any alterations "
                    "that have been made."
                ),
                "min_severity": "low",
            },
            {
                "action": "Consult a digital forensics expert",
                "priority": "medium",
                "description": (
                    "For high-stakes situations, engage a digital forensics professional "
                    "who can perform advanced analysis to conclusively determine whether "
                    "the image has been manipulated."
                ),
                "min_severity": "critical",
            },
        ],

        # ---------------------------------------------------------------
        # Prompt Injection
        # ---------------------------------------------------------------
        "prompt_injection": [
            {
                "action": "Sanitize and reject this input",
                "priority": "immediate",
                "description": (
                    "This input contains patterns designed to manipulate AI systems. "
                    "It should be sanitized or rejected before being processed by any "
                    "language model."
                ),
                "min_severity": "low",
            },
            {
                "action": "Block this input from reaching the AI system",
                "priority": "immediate",
                "description": (
                    "Implement input filtering to prevent this and similar injection "
                    "attempts from being passed to your AI system's prompt pipeline."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Review and strengthen AI system prompts",
                "priority": "high",
                "description": (
                    "Review your AI system's system prompts and instructions to ensure "
                    "they include clear boundaries and cannot be overridden by user input. "
                    "Consider adding explicit refusal instructions."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Add input validation and length limits",
                "priority": "high",
                "description": (
                    "Implement input validation rules including maximum length limits, "
                    "character restrictions, and pattern-based filtering to reduce the "
                    "attack surface for injection attempts."
                ),
                "min_severity": "high",
            },
            {
                "action": "Log and monitor for repeated injection attempts",
                "priority": "medium",
                "description": (
                    "Set up logging and alerting for detected injection patterns. "
                    "Repeated attempts from the same source may indicate a targeted "
                    "attack requiring further investigation."
                ),
                "min_severity": "low",
            },
        ],

        # ---------------------------------------------------------------
        # Anomalous Behavior
        # ---------------------------------------------------------------
        "anomalous_behavior": [
            {
                "action": "Force an immediate password reset",
                "priority": "immediate",
                "description": (
                    "The login patterns suggest possible account compromise. Force a "
                    "password reset for the affected account immediately and ensure "
                    "the new password is strong and unique."
                ),
                "min_severity": "high",
            },
            {
                "action": "Enable multi-factor authentication (MFA)",
                "priority": "immediate",
                "description": (
                    "If not already enabled, activate multi-factor authentication on "
                    "the account to add a second layer of verification beyond the password."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Temporarily lock the account",
                "priority": "immediate",
                "description": (
                    "Suspend the account pending investigation to prevent further "
                    "unauthorized access while the anomalous activity is reviewed."
                ),
                "min_severity": "critical",
            },
            {
                "action": "Investigate recent account activity",
                "priority": "high",
                "description": (
                    "Review all recent activity on the account including file access, "
                    "data exports, configuration changes, and email forwarding rules "
                    "to assess the scope of potential compromise."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Review and revoke active sessions",
                "priority": "high",
                "description": (
                    "Terminate all active sessions for this account across all devices "
                    "and services to ensure any unauthorized access is immediately cut off."
                ),
                "min_severity": "high",
            },
            {
                "action": "Monitor the account for continued anomalies",
                "priority": "medium",
                "description": (
                    "Place the account under enhanced monitoring for the next 30 days "
                    "to detect any continued suspicious activity or re-compromise attempts."
                ),
                "min_severity": "low",
            },
        ],

        # ---------------------------------------------------------------
        # AI-Generated Content
        # ---------------------------------------------------------------
        "ai_generated_content": [
            {
                "action": "Verify the authorship of this content",
                "priority": "high",
                "description": (
                    "This text shows patterns consistent with AI generation. Verify "
                    "the claimed author actually wrote this content, especially if "
                    "authenticity is important for your use case."
                ),
                "min_severity": "low",
            },
            {
                "action": "Cross-reference claims with trusted sources",
                "priority": "high",
                "description": (
                    "AI-generated text may contain plausible-sounding but inaccurate "
                    "information. Independently verify any factual claims, statistics, "
                    "or references against trusted primary sources."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Flag this content for editorial review",
                "priority": "medium",
                "description": (
                    "If this content will be published or used in official communications, "
                    "have it reviewed by a human editor who can verify accuracy, "
                    "originality, and appropriate disclosure of AI involvement."
                ),
                "min_severity": "medium",
            },
            {
                "action": "Check for plagiarism and content originality",
                "priority": "medium",
                "description": (
                    "Run this text through plagiarism detection tools to ensure it does "
                    "not reproduce copyrighted material, as AI models can sometimes "
                    "generate text closely resembling their training data."
                ),
                "min_severity": "high",
            },
            {
                "action": "Add AI-generation disclosure if publishing",
                "priority": "low",
                "description": (
                    "If this content is to be published, consider adding a disclosure "
                    "note indicating it may have been generated or assisted by AI, in "
                    "line with transparency best practices."
                ),
                "min_severity": "low",
            },
        ],
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_recommendations(
        self,
        threat_type: str,
        severity: str,
        features: dict,
    ) -> List[Dict[str, str]]:
        """Generate prioritised recommendations for the detected threat.

        Args:
            threat_type: Category of threat (e.g. 'phishing', 'deepfake').
            severity: Severity label ('critical', 'high', 'medium', 'low', 'safe').
            features: Dict of feature names to observed values (used for
                context-aware filtering).

        Returns:
            A list of 3-5 recommendation dicts, each with 'action',
            'priority', and 'description' keys.
        """
        severity_level = self._SEVERITY_ORDER.get(severity, 0)

        # Normalise sub-types to base type (e.g. deepfake_video -> deepfake)
        base_type = threat_type.split("_")[0] if "_" in threat_type else threat_type
        # Get the recommendation pool for this threat type
        pool = self._RECOMMENDATIONS.get(threat_type) or self._RECOMMENDATIONS.get(base_type, [])

        if not pool:
            return self._generic_recommendations(severity)

        # Filter recommendations by minimum severity threshold
        eligible = []
        for rec in pool:
            min_sev = rec.get("min_severity", "low")
            if severity_level >= self._SEVERITY_ORDER.get(min_sev, 0):
                eligible.append({
                    "action": rec["action"],
                    "priority": rec["priority"],
                    "description": rec["description"],
                })

        # Escalate priorities for higher severity levels
        if severity in ("critical", "high"):
            eligible = self._escalate_priorities(eligible, severity)

        # Sort by priority (immediate > high > medium > low)
        priority_order = {"immediate": 0, "high": 1, "medium": 2, "low": 3}
        eligible.sort(key=lambda r: priority_order.get(r["priority"], 4))

        # Return 3-5 recommendations
        if len(eligible) < 3:
            eligible.extend(self._generic_recommendations(severity))

        return eligible[:5]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _escalate_priorities(
        recommendations: List[Dict[str, str]],
        severity: str,
    ) -> List[Dict[str, str]]:
        """Bump priority levels up for high/critical severity threats."""
        escalation_map = {
            "critical": {"low": "medium", "medium": "high", "high": "immediate"},
            "high": {"low": "medium", "medium": "high"},
        }
        mapping = escalation_map.get(severity, {})

        escalated = []
        for rec in recommendations:
            new_rec = dict(rec)
            current_priority = new_rec["priority"]
            if current_priority in mapping:
                new_rec["priority"] = mapping[current_priority]
            escalated.append(new_rec)

        return escalated

    @staticmethod
    def _generic_recommendations(severity: str) -> List[Dict[str, str]]:
        """Provide generic security recommendations when no specific ones apply."""
        recommendations = [
            {
                "action": "Document and log this incident",
                "priority": "medium",
                "description": (
                    "Record the details of this detection for future reference "
                    "and trend analysis. Include timestamps, input data, and "
                    "the risk score."
                ),
            },
            {
                "action": "Review your security policies",
                "priority": "low",
                "description": (
                    "Use this detection as an opportunity to review and update "
                    "your organisation's security policies and awareness training."
                ),
            },
            {
                "action": "Stay vigilant and report suspicious activity",
                "priority": "low",
                "description": (
                    "Remain alert for similar threats and report any suspicious "
                    "activity to your security team promptly."
                ),
            },
        ]

        if severity in ("critical", "high"):
            for rec in recommendations:
                if rec["priority"] == "low":
                    rec["priority"] = "medium"

        return recommendations
