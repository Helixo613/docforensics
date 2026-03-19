// lib/models/v2_models.dart

class IssueMapResponse {
  final String sessionId;
  final String source;
  final V2Stats stats;
  final V2Coverage coverage;
  final V2Fallback fallback;
  final List<Issue> issues;

  IssueMapResponse({
    required this.sessionId,
    required this.source,
    required this.stats,
    required this.coverage,
    required this.fallback,
    required this.issues,
  });

  factory IssueMapResponse.fromJson(Map<String, dynamic> json) {
    return IssueMapResponse(
      sessionId: json['session_id'] ?? '',
      source: json['source'] ?? 'v2_issue_map',
      stats: V2Stats.fromJson(json['stats'] ?? {}),
      coverage: V2Coverage.fromJson(json['coverage'] ?? {}),
      fallback: V2Fallback.fromJson(json['fallback'] ?? {}),
      issues: (json['issues'] as List<dynamic>?)
              ?.map((i) => Issue.fromJson(i))
              .toList() ??
          [],
    );
  }
}

class V2Stats {
  final int totalIssues;
  final int totalClaims;
  final int contestedIssues;
  final int alignedIssues;
  final int mixedIssues;
  final int unclearIssues;

  V2Stats({
    required this.totalIssues,
    required this.totalClaims,
    required this.contestedIssues,
    required this.alignedIssues,
    required this.mixedIssues,
    required this.unclearIssues,
  });

  factory V2Stats.fromJson(Map<String, dynamic> json) {
    return V2Stats(
      totalIssues: json['total_issues'] ?? 0,
      totalClaims: json['total_claims'] ?? 0,
      contestedIssues: json['contested_issues'] ?? 0,
      alignedIssues: json['aligned_issues'] ?? 0,
      mixedIssues: json['mixed_issues'] ?? 0,
      unclearIssues: json['unclear_issues'] ?? 0,
    );
  }
}

class V2Coverage {
  final int pairDerivedClaimsTotal;
  final int pairDerivedClaimsRepresentedInIssues;
  final int pairRelationsTotal;
  final int pairRelationsRepresentedInIssues;
  final int structurallyAmbiguousClaimsInIssues;
  final int uncorroboratedClaimsOutsideIssueMap;

  V2Coverage({
    required this.pairDerivedClaimsTotal,
    required this.pairDerivedClaimsRepresentedInIssues,
    required this.pairRelationsTotal,
    required this.pairRelationsRepresentedInIssues,
    required this.structurallyAmbiguousClaimsInIssues,
    required this.uncorroboratedClaimsOutsideIssueMap,
  });

  factory V2Coverage.fromJson(Map<String, dynamic> json) {
    return V2Coverage(
      pairDerivedClaimsTotal: json['pair_derived_claims_total'] ?? 0,
      pairDerivedClaimsRepresentedInIssues: json['pair_derived_claims_represented_in_issues'] ?? 0,
      pairRelationsTotal: json['pair_relations_total'] ?? 0,
      pairRelationsRepresentedInIssues: json['pair_relations_represented_in_issues'] ?? 0,
      structurallyAmbiguousClaimsInIssues: json['structurally_ambiguous_claims_in_issues'] ?? 0,
      uncorroboratedClaimsOutsideIssueMap: json['uncorroborated_claims_outside_issue_map'] ?? 0,
    );
  }

  double get claimCoverage {
    if (pairDerivedClaimsTotal == 0) return 0.0;
    return pairDerivedClaimsRepresentedInIssues / pairDerivedClaimsTotal;
  }
}

class V2Fallback {
  final bool shouldFallback;
  final List<String> reasons;
  final double dominantIssueShare;
  final double singletonIssueRatio;

  V2Fallback({
    required this.shouldFallback,
    required this.reasons,
    required this.dominantIssueShare,
    required this.singletonIssueRatio,
  });

  factory V2Fallback.fromJson(Map<String, dynamic> json) {
    return V2Fallback(
      shouldFallback: json['should_fallback'] ?? false,
      reasons: (json['reasons'] as List<dynamic>?)?.map((r) => r.toString()).toList() ?? [],
      dominantIssueShare: (json['dominant_issue_share'] ?? 0.0).toDouble(),
      singletonIssueRatio: (json['singleton_issue_ratio'] ?? 0.0).toDouble(),
    );
  }
}

class Issue {
  final String issueId;
  final String status; // contested | aligned | mixed | unclear
  final String label;
  final String labelKind;
  final String labelClaimId;
  final String structuralQuality; // clean | borderline | weak
  final bool mergeRisk;
  final List<String> documentsInvolved;
  final List<Side> sides;
  final List<V2Claim> mixedClaims;
  final List<V2Claim> unclearClaims;

  Issue({
    required this.issueId,
    required this.status,
    required this.label,
    required this.labelKind,
    required this.labelClaimId,
    required this.structuralQuality,
    required this.mergeRisk,
    required this.documentsInvolved,
    required this.sides,
    required this.mixedClaims,
    required this.unclearClaims,
  });

  factory Issue.fromJson(Map<String, dynamic> json) {
    return Issue(
      issueId: json['issue_id'] ?? '',
      status: json['status'] ?? 'unclear',
      label: json['label'] ?? '',
      labelKind: json['label_kind'] ?? '',
      labelClaimId: json['label_claim_id'] ?? '',
      structuralQuality: json['structural_quality'] ?? 'weak',
      mergeRisk: json['merge_risk'] ?? false,
      documentsInvolved: (json['documents_involved'] as List<dynamic>?)
              ?.map((d) => d.toString())
              .toList() ??
          [],
      sides: (json['sides'] as List<dynamic>?)
              ?.map((s) => Side.fromJson(s))
              .toList() ??
          [],
      mixedClaims: (json['mixed_claims'] as List<dynamic>?)
              ?.map((c) => V2Claim.fromJson(c))
              .toList() ??
          [],
      unclearClaims: (json['unclear_claims'] as List<dynamic>?)
              ?.map((c) => V2Claim.fromJson(c))
              .toList() ??
          [],
    );
  }
}

class Side {
  final String sideId;
  final List<String> documents;
  final List<V2Claim> claims;

  Side({
    required this.sideId,
    required this.documents,
    required this.claims,
  });

  factory Side.fromJson(Map<String, dynamic> json) {
    return Side(
      sideId: json['side_id'] ?? '',
      documents: (json['documents'] as List<dynamic>?)?.map((d) => d.toString()).toList() ?? [],
      claims: (json['claims'] as List<dynamic>?)?.map((c) => V2Claim.fromJson(c)).toList() ?? [],
    );
  }
}

class V2Claim {
  final String claimId;
  final String text;
  final String docName;
  final int page;

  V2Claim({
    required this.claimId,
    required this.text,
    required this.docName,
    required this.page,
  });

  factory V2Claim.fromJson(Map<String, dynamic> json) {
    return V2Claim(
      claimId: json['claim_id'] ?? '',
      text: json['text'] ?? '',
      docName: json['doc_name'] ?? '',
      page: json['page'] ?? 0,
    );
  }
}
