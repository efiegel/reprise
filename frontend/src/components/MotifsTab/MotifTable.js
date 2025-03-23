import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Box,
} from "@mui/material";
import { motifService } from "../../services/motifService";

export default function MotifTable({
  motifs,
  deleteEnabled,
  showClozeDeletions,
  hoveredClozeSet,
  setHoveredClozeSet,
  onOpenModal,
  onMotifUpdate,
  onMotifDelete,
}) {
  const handleContentEditableInput = (e, motifId) => {
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const caretOffset = range.startOffset;

    const newContent = e.target.innerText;
    const updatedMotif = motifs.find((m) => m.uuid === motifId);
    if (updatedMotif) {
      updatedMotif.content = newContent;
      onMotifUpdate(updatedMotif);
    }

    // Restore caret position
    window.requestAnimationFrame(() => {
      const newRange = document.createRange();
      newRange.setStart(
        e.target.firstChild,
        Math.min(caretOffset, newContent.length)
      );
      newRange.collapse(true);
      selection.removeAllRanges();
      selection.addRange(newRange);
    });
  };

  const handleContentEditableBlur = (e, motifId) => {
    const newContent = e.target.innerText;
    motifService.updateMotif(motifId, newContent).catch((error) => {
      console.error("Error updating motif:", error);
    });
  };

  const handleDelete = (uuid) => {
    motifService
      .deleteMotif(uuid)
      .then(() => {
        onMotifDelete(uuid);
      })
      .catch((error) => {
        console.error("Error deleting motif:", error);
      });
  };

  const renderClozeDeletions = (motifId, content, clozeDeletions) => {
    if (!clozeDeletions || clozeDeletions.length === 0) return "";

    return clozeDeletions
      .map(({ uuid, mask_tuples: set }, index) => (
        <span
          key={uuid || index}
          onMouseEnter={() => setHoveredClozeSet({ motifId, set })}
          onMouseLeave={() => setHoveredClozeSet({ motifId: null, set: null })}
          onClick={() =>
            onOpenModal(
              motifs.find((m) => m.uuid === motifId),
              set,
              uuid
            )
          }
          style={{
            cursor: "pointer",
            textDecoration: "underline",
            color: "gray",
            marginRight: "5px",
          }}
        >
          cloze-deletion-{index + 1}
        </span>
      ))
      .reduce(
        (prev, curr, index) => (index === 0 ? [curr] : [...prev, ", ", curr]),
        []
      );
  };

  const renderHighlightedContent = (motifId, content) => {
    if (!hoveredClozeSet.set || hoveredClozeSet.motifId !== motifId) {
      return content;
    }

    const highlightedIndexes = new Set(
      hoveredClozeSet.set.flatMap(([start, end]) =>
        Array.from({ length: end - start + 1 }, (_, i) => start + i)
      )
    );

    return content.split("").map((char, index) => (
      <span
        key={index}
        style={{
          backgroundColor: highlightedIndexes.has(index)
            ? "gray"
            : "transparent",
        }}
      >
        {char}
      </span>
    ));
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell sx={{ width: "50%" }}>Content</TableCell>
            <TableCell sx={{ width: "20%" }}>Citation</TableCell>
            <TableCell sx={{ width: "20%" }}>Created At</TableCell>
            {deleteEnabled && (
              <TableCell sx={{ width: "10%" }}>Actions</TableCell>
            )}
          </TableRow>
        </TableHead>
        <TableBody>
          {motifs.map((motif) => (
            <TableRow key={motif.uuid}>
              <TableCell>
                <div
                  contentEditable
                  suppressContentEditableWarning
                  style={{
                    borderRadius: "4px",
                    padding: "8px",
                    minHeight: "60px",
                    whiteSpace: "pre-wrap",
                    overflowWrap: "break-word",
                  }}
                  onInput={(e) => handleContentEditableInput(e, motif.uuid)}
                  onBlur={(e) => handleContentEditableBlur(e, motif.uuid)}
                >
                  {hoveredClozeSet.motifId === motif.uuid
                    ? renderHighlightedContent(motif.uuid, motif.content)
                    : motif.content}
                </div>
                {showClozeDeletions && (
                  <Box mt={1} display="flex" alignItems="center">
                    <Box>
                      {renderClozeDeletions(
                        motif.uuid,
                        motif.content,
                        motif.cloze_deletions
                      )}
                    </Box>
                    <Button
                      size="small"
                      onClick={() => onOpenModal(motif, [])}
                      sx={{ ml: 2 }}
                    >
                      + add
                    </Button>
                  </Box>
                )}
              </TableCell>
              <TableCell>{motif.citation}</TableCell>
              <TableCell>
                {new Date(motif.created_at).toLocaleString()}
              </TableCell>
              {deleteEnabled && (
                <TableCell>
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={() => handleDelete(motif.uuid)}
                  >
                    Delete
                  </Button>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
