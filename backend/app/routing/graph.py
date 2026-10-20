import networkx as nx
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.models import RoadSegment, RiskScore

class CorridorGraph:
    def __init__(self, corridor: str = "NH-10"):
        self.corridor = corridor
        self.graph = nx.DiGraph()

    def build_from_db(self, db: Session):
        self.graph.clear()
        segments = db.query(RoadSegment).filter(RoadSegment.corridor == self.corridor).all()

        for seg in segments:
            risk = seg.risk_score
            score = risk.risk_score if risk else 0.1
            label = risk.risk_label if risk else "open"

            # Add forward and reverse edges for two-way highway traffic
            # u -> v
            self.graph.add_edge(
                seg.start_node,
                seg.end_node,
                segment_id=seg.id,
                edge_id=seg.edge_id,
                length_m=seg.length_m,
                base_time_sec=seg.base_travel_time_sec,
                risk_score=score,
                risk_label=label,
                explanation=risk.explanation if risk else "",
                coordinates=seg.coordinates_json
            )
            # v -> u (reverse coordinates for reverse path)
            rev_coords = list(reversed(seg.coordinates_json))
            self.graph.add_edge(
                seg.end_node,
                seg.start_node,
                segment_id=seg.id,
                edge_id=f"{seg.edge_id}_rev",
                length_m=seg.length_m,
                base_time_sec=seg.base_travel_time_sec,
                risk_score=score,
                risk_label=label,
                explanation=risk.explanation if risk else "",
                coordinates=rev_coords
            )

        return self.graph
