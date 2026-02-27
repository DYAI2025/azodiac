import re
from typing import List, Dict, Set
from .schemas import MarkerRegistry, AnalysisResult, DetectedMarker, VADWeights, ATOSignal, SEMMarker

class DetectionEngine:
    def __init__(self, registry: MarkerRegistry):
        self.registry = registry
        # Compile patterns for performance
        self.ato_patterns = {
            ato.id: re.compile(ato.pattern) for ato in registry.atos
        }

    def analyze(self, text: str) -> AnalysisResult:
        result = AnalysisResult(text=text)
        
        # Phase 1: ATO Detection
        detected_atos: List[DetectedMarker] = []
        ato_ids_hit: Set[str] = set()
        
        for ato in self.registry.atos:
            pattern = self.ato_patterns.get(ato.id)
            if not pattern:
                continue
                
            for match in pattern.finditer(text):
                detected = DetectedMarker(
                    id=ato.id,
                    span=[match.start(), match.end()],
                    text=match.group(),
                    vad=ato.vad
                )
                detected_atos.append(detected)
                ato_ids_hit.add(ato.id)
        
        result.atos = detected_atos

        # Phase 2: SEM Logic
        detected_sems: List[DetectedMarker] = []
        sem_ids_hit: Set[str] = set()
        
        for sem in self.registry.sems:
            hit = False
            # Logic implementation
            if sem.logic == "OR":
                hit = any(ato_id in ato_ids_hit for ato_id in sem.constituent_atos)
            elif sem.logic == "AND":
                hit = all(ato_id in ato_ids_hit for ato_id in sem.constituent_atos)
            # SEQUENCE logic is a placeholder for future complex temporal matching
            
            if hit:
                # Find the bounding span of constituent ATOs if possible
                constituent_spans = [a.span for a in detected_atos if a.id in sem.constituent_atos]
                if constituent_spans:
                    start = min(s[0] for s in constituent_spans)
                    end = max(s[1] for s in constituent_spans)
                    detected_sems.append(DetectedMarker(
                        id=sem.id,
                        span=[start, end],
                        text=text[start:end]
                    ))
                    sem_ids_hit.add(sem.id)

        result.sems = detected_sems

        # Phase 3: CLU Aggregation
        detected_clus: List[DetectedMarker] = []
        for clu in self.registry.clus:
            if any(sem_id in sem_ids_hit for sem_id in clu.markers):
                # CLU covers all markers contributing to it
                constituent_spans = [s.span for s in detected_sems if s.id in clu.markers]
                if constituent_spans:
                    start = min(s[0] for s in constituent_spans)
                    end = max(s[1] for s in constituent_spans)
                    detected_clus.append(DetectedMarker(
                        id=clu.id,
                        span=[start, end],
                        text=text[start:end]
                    ))
        
        result.clus = detected_clus

        # Phase 4: VAD Scoring
        total_v = 0.0
        total_a = 0.0
        total_d = 0.0
        count = 0
        
        for ato in detected_atos:
            total_v += ato.vad.valence
            total_a += ato.vad.arousal
            total_d += ato.vad.dominance
            count += 1
            
        if count > 0:
            result.vad_score = VADWeights(
                valence=round(total_v / count, 3),
                arousal=round(total_a / count, 3),
                dominance=round(total_d / count, 3)
            )
            
        return result
