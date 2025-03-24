import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  Button,
  Typography,
} from "@mui/material";

export default function ReprisalTable({
  reprisals,
  unmaskedRows,
  onToggleUnmask,
}) {
  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableBody>
          {reprisals.map((reprisal) => (
            <TableRow key={reprisal.uuid}>
              <TableCell>
                {unmaskedRows[reprisal.uuid] && reprisal.cloze_deletions
                  ? // Render unmasked content with bold and green for masked sections
                    reprisal.cloze_deletions
                      .flatMap((cd) => cd.mask_tuples)
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
                          reprisal.cloze_deletions
                            .flatMap((cd) => cd.mask_tuples)
                            .at(-1)[1] + 1
                        )
                      )
                  : reprisal.maskedContent}
              </TableCell>
              <TableCell>{reprisal.citation}</TableCell>
              <TableCell>
                {reprisal.cloze_deletions && (
                  <Button
                    variant="outlined"
                    onClick={() => onToggleUnmask(reprisal.uuid)}
                  >
                    {unmaskedRows[reprisal.uuid] ? "Mask" : "Unmask"}
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
