import React from "react";
import { Box, Button, Modal, Typography } from "@mui/material";

export default function ClozeDeletionModal({
  open,
  motif,
  selectedBins,
  onClose,
  onSave,
  onDelete,
  onMouseDown,
  onMouseEnter,
  onMouseUp,
}) {
  if (!motif) return null;

  const renderBins = (content) => {
    return content.split("").map((char, index) => (
      <span
        key={index}
        onMouseDown={() => onMouseDown(index)}
        onMouseEnter={() => onMouseEnter(index)}
        onMouseUp={onMouseUp}
        style={{
          display: "inline-block",
          padding: "2px 4px",
          margin: "1px",
          borderRadius: "4px",
          backgroundColor: selectedBins.has(index) ? "gray" : "transparent",
          cursor: "pointer",
          userSelect: "none",
        }}
      >
        {char}
      </span>
    ));
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Box
        sx={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 400,
          bgcolor: "background.paper",
          boxShadow: 24,
          p: 4,
          borderRadius: 2,
        }}
        onMouseLeave={() => onMouseUp()} // Ensure dragging stops when leaving the modal
      >
        <Box
          mb={2}
          sx={{
            whiteSpace: "pre-wrap",
            wordWrap: "break-word",
            border: "1px solid #ccc",
            padding: "8px",
            borderRadius: "4px",
            cursor: "pointer",
          }}
          onMouseUp={onMouseUp} // Ensure dragging stops when releasing the mouse
        >
          {motif && renderBins(motif.content)}
        </Box>
        <Typography variant="body2" mb={2}>
          Click and drag over the text to select or deselect sections for a
          cloze deletion set.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={onSave}
          sx={{ mr: 1 }}
        >
          Save
        </Button>
        {motif?.clozeDeletionUuid && (
          <Button
            variant="contained"
            color="secondary"
            onClick={onDelete}
            sx={{ mr: 1 }}
          >
            Delete
          </Button>
        )}
        <Button variant="outlined" onClick={onClose}>
          Cancel
        </Button>
      </Box>
    </Modal>
  );
}
