import { useState, useEffect } from "react";
import { fetchCitations, addCitation } from "../services/citationService";

export const useCitations = () => {
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCitations = async () => {
    setLoading(true);
    try {
      const data = await fetchCitations();
      setCitations(data || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching citations:", err);
      setError("Failed to load citations");
      setCitations([]);
    } finally {
      setLoading(false);
    }
  };

  const createCitation = async (title) => {
    try {
      const newCitation = await addCitation(title);
      setCitations((prev) => [...prev, newCitation]);
      return newCitation;
    } catch (err) {
      console.error("Error adding citation:", err);
      setError("Failed to add citation");
      return null;
    }
  };

  useEffect(() => {
    loadCitations();
  }, []);

  return {
    citations,
    loading,
    error,
    loadCitations,
    createCitation,
  };
};
