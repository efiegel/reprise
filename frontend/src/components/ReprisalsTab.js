import React, { useState, useEffect } from "react";
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  Button,
  CircularProgress,
} from "@mui/material";

const applyMasking = (content, maskTuples, mask) => {
  let maskedContent = content;
  let nRemovedCharacters = 0;

  maskTuples.forEach(([start, end]) => {
    start -= nRemovedCharacters;
    end -= nRemovedCharacters;

    maskedContent =
      maskedContent.slice(0, start) + mask + maskedContent.slice(end + 1);
    nRemovedCharacters += end - start + 1 - mask.length;
  });

  return maskedContent;
};

export default function ReprisalsTab() {
  const [reprisals, setReprisals] = useState([]);
  const [repriseLoading, setRepriseLoading] = useState(false);

  const fetchReprisals = () => {
    setRepriseLoading(true);
    fetch("http://127.0.0.1:5000/reprise", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const processedData = data.map((reprisal) => ({
          ...reprisal,
          content: reprisal.cloze_deletions
            ? applyMasking(reprisal.content, reprisal.cloze_deletions, " ___ ")
            : reprisal.content,
        }));
        setReprisals(processedData);
        setRepriseLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching reprisals:", error);
        setRepriseLoading(false);
      });
  };

  useEffect(() => {
    // Automatically fetch a new set of reprisals on mount
    fetchReprisals();
  }, []);

  return (
    <Box>
      {reprisals.length > 0 && (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableBody>
              {reprisals.map((reprisal) => (
                <TableRow key={reprisal.uuid}>
                  <TableCell>{reprisal.content}</TableCell>
                  <TableCell>{reprisal.citation}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      <Button
        variant="contained"
        color="primary"
        onClick={fetchReprisals}
        disabled={repriseLoading}
        sx={{ mt: 3 }}
      >
        {repriseLoading ? <CircularProgress size={24} /> : "Generate"}
      </Button>
    </Box>
  );
}
