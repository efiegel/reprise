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
  Typography,
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
  const [unmaskedRows, setUnmaskedRows] = useState({}); // Track unmasked rows by UUID

  const toggleUnmask = (uuid) => {
    setUnmaskedRows((prev) => ({
      ...prev,
      [uuid]: !prev[uuid],
    }));
  };

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
          maskedContent: reprisal.cloze_deletions
            ? applyMasking(reprisal.content, reprisal.cloze_deletions, " ___ ")
            : reprisal.content,
          originalContent: reprisal.content, // Store the original unmasked content
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
                  <TableCell>
                    {unmaskedRows[reprisal.uuid]
                      ? // Render unmasked content with bold and green for masked sections
                        reprisal.cloze_deletions
                          .reduce(
                            (acc, [start, end], index) => {
                              const before = reprisal.originalContent.slice(
                                acc.lastIndex,
                                start
                              );
                              const unmasked = reprisal.originalContent.slice(
                                start,
                                end + 1
                              );
                              acc.elements.push(
                                <span key={`before-${index}`}>{before}</span>
                              );
                              acc.elements.push(
                                <Typography
                                  key={`unmasked-${index}`}
                                  component="span"
                                  sx={{ color: "green", fontWeight: "bold" }}
                                >
                                  {unmasked}
                                </Typography>
                              );
                              acc.lastIndex = end + 1;
                              return acc;
                            },
                            { elements: [], lastIndex: 0 }
                          )
                          .elements.concat(
                            reprisal.originalContent.slice(
                              reprisal.cloze_deletions.at(-1)[1] + 1
                            )
                          )
                      : reprisal.maskedContent}
                  </TableCell>
                  <TableCell>{reprisal.citation}</TableCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      onClick={() => toggleUnmask(reprisal.uuid)}
                    >
                      {unmaskedRows[reprisal.uuid] ? "Mask" : "Unmask"}
                    </Button>
                  </TableCell>
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
