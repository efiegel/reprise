import React from "react";
import { Box, CircularProgress, Alert } from "@mui/material";
import { useCitations } from "../hooks/useCitations";
import { AddCitationForm } from "./CitationsTab/AddCitationForm";
import { CitationsTable } from "./CitationsTab/CitationsTable";

export default function CitationsTab() {
  const { citations, loading, error, createCitation } = useCitations();

  const handleAddCitation = async (title) => {
    return await createCitation(title);
  };

  return (
    <Box>
      <AddCitationForm onAddCitation={handleAddCitation} />

      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}

      {!loading && citations.length > 0 && (
        <CitationsTable citations={citations} />
      )}

      {!loading && citations.length === 0 && !error && (
        <Box mt={2}>No citations available.</Box>
      )}
    </Box>
  );
}
