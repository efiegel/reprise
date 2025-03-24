import React, { useEffect } from "react";
import { Box, Button, CircularProgress } from "@mui/material";
import { useReprisals } from "../hooks/useReprisals";
import ReprisalTable from "./ReprisalsTab/ReprisalTable";

export default function ReprisalsTab() {
  const { reprisals, isLoading, unmaskedRows, toggleUnmask, fetchReprisals } =
    useReprisals();

  useEffect(() => {
    // Automatically fetch a new set of reprisals on mount
    fetchReprisals();
  }, []);

  return (
    <Box>
      {reprisals.length > 0 && (
        <ReprisalTable
          reprisals={reprisals}
          unmaskedRows={unmaskedRows}
          onToggleUnmask={toggleUnmask}
        />
      )}
      <Button
        variant="contained"
        color="primary"
        onClick={fetchReprisals}
        disabled={isLoading}
        sx={{ mt: 3 }}
      >
        {isLoading ? <CircularProgress size={24} /> : "Generate"}
      </Button>
    </Box>
  );
}
