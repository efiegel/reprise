import { useState } from "react";
import { reprisalService } from "../services/reprisalService";
import { applyMasking } from "../utils/maskingUtils";

export function useReprisals() {
  const [reprisals, setReprisals] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [unmaskedRows, setUnmaskedRows] = useState({});

  const toggleUnmask = (uuid) => {
    setUnmaskedRows((prev) => ({
      ...prev,
      [uuid]: !prev[uuid],
    }));
  };

  const fetchReprisals = async () => {
    setIsLoading(true);
    try {
      const data = await reprisalService.getReprisals();
      const processedData = data.map((reprisal) => ({
        ...reprisal,
        maskedContent: reprisal.cloze_deletions
          ? applyMasking(
              reprisal.content,
              reprisal.cloze_deletions.flatMap((cd) => cd.mask_tuples),
              " ___ "
            )
          : reprisal.content,
        originalContent: reprisal.content, // Store the original unmasked content
      }));
      setReprisals(processedData);
    } catch (error) {
      console.error("Error fetching reprisals:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    reprisals,
    isLoading,
    unmaskedRows,
    toggleUnmask,
    fetchReprisals,
  };
}
