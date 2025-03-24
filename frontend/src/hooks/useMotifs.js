import { useState, useCallback } from "react";
import { motifService } from "../services/motifService";

export function useMotifs(page, pageSize) {
  const [motifs, setMotifs] = useState([]);
  const [citations, setCitations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalMotifs, setTotalMotifs] = useState(0);
  const [hoveredClozeSet, setHoveredClozeSet] = useState({
    motifId: null,
    set: null,
  });

  const fetchMotifs = useCallback(() => {
    setIsLoading(true);

    Promise.all([
      motifService.getMotifs(page, pageSize),
      motifService.getCitations(),
    ])
      .then(([motifsData, citationsData]) => {
        setMotifs(motifsData.motifs || []);
        setTotalMotifs(motifsData.total_count || 0);
        setCitations(citationsData || []);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setMotifs([]);
        setTotalMotifs(0);
        setCitations([]);
        setIsLoading(false);
      });
  }, [page, pageSize]);

  return {
    motifs,
    setMotifs,
    citations,
    isLoading,
    totalMotifs,
    hoveredClozeSet,
    setHoveredClozeSet,
    fetchMotifs,
  };
}
