"""Unit tests for AI prompt contracts, domain knowledge scope, and system prompt structure."""

import unittest

from ai.prompts import (
    AES_CONTRACT,
    CAPABILITIES,
    CHAT_CONTRACT,
    CLARIFICATION_CONTRACT,
    DOMAIN_SCOPE,
    DOUBLE_DES_CONTRACT,
    IDENTITY,
    RESPONSE_RULES,
    RSA_CONTRACT,
    RULES,
    SYSTEM_PROMPT,
    TOOL_CONTRACT,
    TRIPLE_DES_CONTRACT,
)


class PromptsTests(unittest.TestCase):
    """Verify that system prompt and contracts encompass domain scope and execution bounds."""

    def test_identity_includes_dual_role(self) -> None:
        """Identity should define both workstation operator and domain specialist roles."""
        self.assertIn("WORKSTATION OPERATOR", IDENTITY)
        self.assertIn("CRYPTOGRAPHY DOMAIN SPECIALIST", IDENTITY)

    def test_domain_scope_covers_advanced_cryptography(self) -> None:
        """Domain scope must explicitly include broad cryptographic fields and primitives."""
        self.assertIn("Symmetric Cryptography", DOMAIN_SCOPE)
        self.assertIn("Post-Quantum Cryptography", DOMAIN_SCOPE)
        self.assertIn("Zero-Knowledge Proofs", DOMAIN_SCOPE)
        self.assertIn("Elliptic Curves", DOMAIN_SCOPE)
        self.assertIn("TLS 1.3", DOMAIN_SCOPE)
        self.assertIn("ChaCha20", DOMAIN_SCOPE)
        self.assertIn("Argon2", DOMAIN_SCOPE)

    def test_rules_distinguish_tool_restrictions_from_chat(self) -> None:
        """Rules must restrict services to the 4 engines only for 'tool' action, not chat."""
        self.assertIn("TOOL RESTRICTIONS (action: \"tool\" ONLY)", RULES)
        self.assertIn("REQUESTS FOR UNSUPPORTED TOOLS", RULES)
        self.assertIn("respond with action: \"chat\"", RULES)

    def test_system_prompt_aggregates_all_components(self) -> None:
        """SYSTEM_PROMPT must incorporate DOMAIN_SCOPE and all sub-contracts."""
        self.assertIn(DOMAIN_SCOPE.strip(), SYSTEM_PROMPT)
        self.assertIn(IDENTITY.strip(), SYSTEM_PROMPT)
        self.assertIn(CAPABILITIES.strip(), SYSTEM_PROMPT)
        self.assertIn(RULES.strip(), SYSTEM_PROMPT)
        self.assertIn(RESPONSE_RULES.strip(), SYSTEM_PROMPT)
        self.assertIn(CHAT_CONTRACT.strip(), SYSTEM_PROMPT)
        self.assertIn(CLARIFICATION_CONTRACT.strip(), SYSTEM_PROMPT)
        self.assertIn(TOOL_CONTRACT.strip(), SYSTEM_PROMPT)
        self.assertIn(AES_CONTRACT.strip(), SYSTEM_PROMPT)
        self.assertIn(RSA_CONTRACT.strip(), SYSTEM_PROMPT)
        self.assertIn(DOUBLE_DES_CONTRACT.strip(), SYSTEM_PROMPT)
        self.assertIn(TRIPLE_DES_CONTRACT.strip(), SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
